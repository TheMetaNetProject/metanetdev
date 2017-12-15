'use strict';

/**
 * New node file
 */

var documentControllers = angular.module('documentControllers', ['ngRoute']);

// Managing the document list
documentControllers.controller('DocumentListCtrl', ['$scope', 'Document', 'Collections',
                                                    function($scope, Document, Collections) {
//          console.log('>> in DocumentListCtrl', $scope);

         $scope.delay = 0;
         $scope.minDuration = 0;
         $scope.message = 'Please Wait...';
         $scope.backdrop = true;
         $scope.queryPromise = null;

         $scope.batchSize = 20;

         // Here we receive the results from the query on documents
         var success = function(hit) {
            var docs = hit.docs;
            $scope.docs = docs.map(function(doc) {
//               var doc = d.doc;
               if (! ('lms' in doc)) // JS is really funny
                  doc.lms = []

               return doc;
            });

            if (docs.length > 0) {
               $scope.batchSize = docs.length;
               $scope.firstId   = _.first(docs)._id;
               $scope.lastId    = _.last(docs)._id;

               console.log('firstId:', $scope.firstId);
               console.log('lastId:', $scope.lastId);

               $scope.pairs.push([$scope.firstId, $scope.lastId])
               console.log('pairs:', $scope.pairs);
            }
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
            for (var c in search) {
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

         var typeOf = function(obj) {
            return ({}).toString.call(obj).match(/\s([a-zA-Z]+)/)[1].toLowerCase()
         }

         // Match an LM against selected criteria
         var match = function(lm) {
            var search = $scope.search
            for (var c in search) {
               if (search[c] != '') {
                  if (c != 'score') {
                     var x = objPath(lm, c.split('_'))
                     switch (typeOf(x)) {
                     case 'array':
                        if (_.any(x, function(s) { return x.match(new RegExp(s, 'i')); }))
                           return true;
                        break
                     case 'string':
                        if (x.match(new RegExp(search[c], 'i')))
                           return true;
                        break
                     default:
                        break
                     }
                  }
                  else if (objPath(lm, c.split('_')) > parseFloat(search[c]))
                     return true;
               }
            }
            return false;
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
               });

               // console.log('**segments:', segments.map(function(s) { return s.text; }).join(' '));
               // console.log('**compress:', compressed.map(function(s) { return s.text; }).join(' '));

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

         function makeQuery(search) {
            var terms = Object.keys(search)
               .filter(function(c) {
                  return search[c].length > 0 && c != 'score';
                })
               .map(function(c) {
                  var term = { regexp: {} };
                  term.regexp[c.replace('_', '-')] = search[c];
                  return term;
               });

            return terms ? { filter: { bool: { must: terms } } } : {};
         }

         var do_query = function(startId) {
            console.log('in do_query:', startId);

            var q = makeQuery($scope.search)
            console.log('in do_query: query:', q);

            var promise = Document.query({
                  language: $scope.language.key,
                  size: 20,
                  startId: startId || ' '
               }, q).$promise;
            $scope.queryPromise = promise; // TODO: why do I need this?
            promise.then(success);
         }

         // Changed to collections
         var query_languages = function() {
            Collections.query({})
               .$promise
               .then(function(languages) {
                  $scope.languages = languages;
                  $scope.language = languages[0];
               });
         }

         $scope.prevPage = function() {
//            console.log('>> in DocumentListCtrl, prevPage()');
//            $scope.up = true;
            // Discard the top one
            $scope.pairs.pop()
            do_query($scope.pairs.pop()[0]);
         }

         $scope.nextPage = function() {
           console.log('>> in DocumentListCtrl, nextPage()');
//            $scope.up = true;

            console.log('Querying for is', $scope.lastId);
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

         if ($scope.language === undefined)
            query_languages();

//         $scope.$watch('language', function(_1, language) {
//            console.log('languages set to', language);
//            if (! language === undefined)
//               do_query($scope.firstId);
//         });

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
