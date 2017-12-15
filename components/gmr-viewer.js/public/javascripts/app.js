'use strict';

/**
 * app.js
 */

var gmrViewerApp = angular.module('gmrViewerApp',
    ['ngRoute', 'documentControllers', 'documentServices', 'd3', 'dagreD3', 'documentDirectives', 'cgBusy']);

gmrViewerApp
  .filter('unsafe', function($sce) {
      return function(val) {
          return $sce.trustAsHtml(val);
      }
  })
  .filter('elements', function() {
    return function(input, sep) {
      if (sep) {
        sep = new RegExp(sep, 'i');
        var xs = _.map(input, function(x) { return x.split(sep)[1]; });
        return xs.join(', ');
      }
      else
        return input.length > 0 ? input.join(', ') : '(none)';
     }
  })
  .filter('split', function() {
    return function(input, sep) {
      if (sep === undefined)
        sep = ','
      else
        sep = new RegExp(sep, 'i');
      return input ? input.split(sep) : [];
    }
  });

gmrViewerApp.config(['$routeProvider', function($routeProvider) {
  $routeProvider.when('/docs/', {
    templateUrl: 'partials/docs.html',
    controller: 'DocumentListCtrl'
  });

  $routeProvider.when('/docs/:docId', {
    templateUrl: 'partials/item.html',
    controller: 'DocumentItemCtrl'
  });

  $routeProvider.when('/new', {
    templateUrl: 'partials/new.html',
    controller: 'DocumentNewCtrl'
  });

  $routeProvider.otherwise({
    redirectTo: '/docs'
  });
}]);

gmrViewerApp.constant('_', window._);
