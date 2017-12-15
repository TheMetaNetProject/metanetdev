'use strict';

/*
 * Services.js
 */

var documentServices = angular.module('documentServices', ['ngResource']);

// The module name has to be the same as the Controller's!
documentServices.factory('Document', ['$resource', function($resource) {
   return $resource('docs/:docId/:lang', {}, {
      // Use this method for getting a list of documents
      query: {
         method: 'GET', params: {
//            docId: 'docs', lang: '@lang', file: '@file', n: '@n', batchSize: '@count'
            docId: 'docs', lang: '@lang', _id: '@_id', batchSize: '@count'
         }, 
         isArray: true
      }, 
      item: {
         method: 'GET', params: {
            docId: '@docId'
         }, 
         isArray: false
      }, 
      languages: {
         method: 'GET', params: {
            docId: 'languages'
         }, 
         isArray: true
      }
   });
}]);

var d3Service = angular.module('d3', []);

d3Service.factory('d3Service', ['$document', '$window', '$q', '$rootScope', function($document, $window, $q, $rootScope) {
   console.log('d3Service factory');

   function onScriptLoad() {
      // Load client in the browser
      $rootScope.$apply(function() {
         // console.log('defer', defer);
         defer.resolve($window.d3);
         // console.log('resolved.');
      });
   }
   ;

   var defer = $q.defer();

   // Create a script tag with d3 as the source
   // and call our onScriptLoad callback when it
   // has been loaded
   var scriptTag = $document[0].createElement('script');
   scriptTag.type = 'text/javascript';
//   scriptTag.async = true;
   scriptTag.async = false;
   scriptTag.src = '/components/d3/d3.min.js';
   scriptTag.onreadystatechange = function() {
      if (this.readyState == 'complete')
         onScriptLoad();
   }

   scriptTag.onload = onScriptLoad;

   var s = $document[0].getElementsByTagName('body')[0];
   s.appendChild(scriptTag);

   return {
      d3: function() {
         return defer.promise;
      }
   };
}]);

var dagreD3Service = angular.module('dagreD3', []);

dagreD3Service.factory('dagreD3Service', ['$document', '$window', '$q', '$rootScope', 
                                          function($document, $window, $q, $rootScope) {
   console.log('dagreD3Service factory');
   
   function onScriptLoad() {
      // Load client in the browser
      $rootScope.$apply(function() {
         deferred.resolve($window.dagreD3);
         console.log('dagreD3Service loaded.');
      });
   };
   
   var deferred = $q.defer();
   
   var dagreTag = $document[0].createElement('script');
   dagreTag.type = 'text/javascript';
//   dagreTag.async = true;
   dagreTag.async = false;
   dagreTag.src = '/javascripts/dagre-d3.js';
   dagreTag.onload = onScriptLoad;
   dagreTag.onreadystatechange = function() {
      if (this.readyState == 'complete')
         onScriptLoad();
   }
   
   var s = $document[0].getElementsByTagName('body')[0];
   s.appendChild(dagreTag);
   
   return {
      dagreD3: function() {
         return deferred.promise;
      }
   };
}]);
