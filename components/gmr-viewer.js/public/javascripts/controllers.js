'use strict';

/**
 * New node file
 */

var documentControllers = angular.module('documentControllers', ['ngRoute']);

// Managing the document list
documentControllers.controller('DocumentListCtrl', ['$scope', 'Document', function($scope, Document) {
         // console.log('>> in DocumentListCtrl', $scope);
         
         $scope.delay = 0;
         $scope.minDuration = 0;
         $scope.message = 'Please Wait...';
         $scope.backdrop = true;
         $scope.queryPromise = null;

         // Whether we are going up or down
         $scope.up = true; // TODO: get rid of this
         
//         $scope.firstId = { file: '', n: '' }
//         $scope.lastId = { file: '', n: '' }
//         $scope.firstId = '';
//         $scope.lastId = '';

//         $scope.pairs = []
         $scope.batchSize = 20;
         $scope.languages = [
           { key: 'en', display: 'English' }, 
           { key: 'fa', display: 'Farsi' }, 
           { key: 'es', display: 'Spanish' }, 
           { key: 'ru', display: 'Russian' }
         ];
         
         if ($scope.language === undefined)
            $scope.language = $scope.languages[0];

         var success = function(docs) {
            $scope.docs = docs;
            if (docs.length > 0) {
               $scope.batchSize = docs.length;
//               $scope.firstId = {
//                  file: docs[0].file, n: docs[0].n
//               };
//               $scope.lastId = {
//                  file: docs.slice(-1)[0].file, n: docs.slice(-1)[0].n
//               };
               $scope.firstId = docs[0]._id;
               $scope.lastId = docs.slice(-1)[0]._id;
               
               console.log('firstId:', $scope.firstId);
               console.log('lastId:', $scope.lastId);
            }
            $scope.pairs.push([$scope.firstId, $scope.lastId])
            console.log('pairs:', $scope.pairs.length);
         }

         var searchListener = function(oldValue, newValue) {
             console.log('search:', oldValue, newValue);
             console.log('>>> restting pairs!');
//            $scope.firstId = { file: '', n: ''};
            $scope.firstId = '';
            $scope.pairs = []
         }

         $scope.$watch('search', searchListener, true);

         $scope.searchCriteria = function() {
            var criteria = {};
            var search = $scope.search;
            for ( var c in search) {
               if (search[c] != '') {
                  criteria[c.split('_').join(' ')] = search[c]
               }
            }
            return criteria;
         }

         var highest = function(lms) {
            return lms.sort(function(lm1, lm2) {
               return lm2.score - lm1.score
            })
         }

         $scope.highest = highest

         var objPath = function(obj, path) {
            if (path.length == 0)
               return obj
            else
               return objPath(obj[path[0]], path.slice(1))
         }

         var _typeOf = function(obj) {
            return ({}).toString.call(obj).match(/\s([a-zA-Z]+)/)[1].toLowerCase()
         }

         // Match an LM against selected criteria
         var match = function(lm) {
            var search = $scope.search
            for (var c in search) {
               if (search[c] != '') {
                  if (c != 'score') {
                     var x = objPath(lm, c.split('_'))
                     switch (_typeOf(x)) {
                     case 'array':
                        if (x.indexOf(search[c]) < 0)
                           return false
                        break
                     case 'string':
                        if (search[c] != x)
                           return false
                        break
                     default:
                        break
                     }
                  }
                  else if (parseFloat(search[c]) >= objPath(lm, c.split('_')))
                     return false
               }
            }
            return true
         }

         $scope.match = match

         $scope.highlighted_text = function(doc) {
            var text = doc.text
            if (doc.lms === 'undefined') {
               return text
            }
            else {
               // Collect all the segments
               var hilites = []
               highest(doc.lms.filter(match)).forEach(function(lm) {
                  hilites.push({
                     type: 'source', pair: [lm.source.start, lm.source.end], text: null, name: lm.name
                  })
                  hilites.push({
                     type: 'target', pair: [lm.target.start, lm.target.end], text: null, name: lm.name
                  })
               })

               // Sort them (in place)
               hilites.sort(function(x, y) {
                  return x.pair[0] - y.pair[0]
               })

               // Fill in
               var i = 0;
               var segments = []
               hilites.forEach(function(s) {
                  if (s.pair[0] > i)
                     segments.push({
                        type: null, pair: [i, s.pair[0]], text: text.substring(i, s.pair[0])
                     })
                  s.text = text.substring(s.pair[0], s.pair[1])
                  segments.push(s)
                  i = s.pair[1]
               })

               if (i < text.length) {
                  segments.push({
                     type: null, pair: [i, text.length - 1], text: text.substring(i)
                  });
               } 
               
               // Throw away duplicates
               var pos = -1
               var compressed = segments.filter(function(s) {
                  var different = (s.pair[0] != pos)
                  if (different)
                     pos = s.pair[0]
                  return different
               })
               
//               console.log('**segments:', segments.map(function(s) { return s.text; }).join(' '));
//               console.log('**compress:', compressed.map(function(s) { return s.text; }).join(' '));
               
               // Prepare final HTML
               var html = compressed.map(function(s) {
                  switch (s.type) {
                  case 'source':
                     return '<span class="source-word">' + s.text + '</span>'
                     break
                  case 'target':
                     return '<span class="target-word">' + s.text + '</span>'
                     break
                  default:
                     return s.text
                  }
               })
               return html.join(' ')
            }
         }

         if (!$scope.search)
            $scope.search = {}

         var do_query = function(startId) {
            console.log('in do_query:', startId);

            // First, ask what languages are available in the DB
            query_languages();

//            $scope.docs = [];
            
            var promise = Document.query({
               lang: $scope.language.key,
//               file: startId.file,
//               n: startId.n || 0,
               _id: startId || '',
               batchSize: $scope.batchSize,
               up: $scope.up,
               search: $scope.search
            })
            .$promise
            
            $scope.queryPromise = promise;
            
            promise.then(success);
         }

         var query_languages = function() {
            $scope.languages = [];
            Document.languages({}).$promise.then(function(languages) {
               $scope.languages = languages;
               if (! $scope.language)
                  $scope.language = languages[0];
            });
         }

         $scope.prevPage = function() {
//            console.log('>> in DocumentListCtrl, prevPage()');
            $scope.up = true;
            // Discard the top one
            $scope.pairs.pop()
            do_query($scope.pairs.pop()[0]);
         }

         $scope.nextPage = function() {
//            console.log('>> in DocumentListCtrl, nextPage()');
            $scope.up = true;
            do_query($scope.lastId);
            // $scope.pairs.push([$scope.firstId, $scope.lastId])
         }

         var submitSearch = function() {
            $scope.firstId = '';
            $scope.lastId = '';
            $scope.pairs = []
      
            do_query($scope.firstId);
         };

         $scope.submitSearch = submitSearch;

         do_query($scope.firstId);
      }]);

// Single document
documentControllers.controller('DocumentItemCtrl', ['$scope', 'Document', function($scope, Document) {
   // console.log('>> in DocumentItemCtrl');
   // $scope.doc = Document.item({
   // docId: $routeParams.docId
   // });

   var highest = function(lms) {
      // console.log('lms:', lms);
      return lms.sort(function(lm1, lm2) {
         return lm2.score - lm1.score
      });
   }

   $scope.highest = highest

   var displayListener = function(oldValue, newValue) {
      $scope.$broadcast('display', newValue);
   }

   $scope.$watch(function(scope) { return scope.doc.display; }, displayListener, true);

}]);
