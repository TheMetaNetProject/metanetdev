'use strict';

/**
 * directives.js
 */

var documentDirectives = angular.module('documentDirectives', ['d3'])

documentDirectives.directive('d3DepTree', ['$window', '$timeout', 'd3Service', '_', function($window, $timeout, d3Service, _) {
   return {
      restrict: 'A',
      // scope: {
      // // data: '=',
      // label: '@',
      // onClick: '&'
      // },
      link: function(scope, element, attrs) {
         d3Service.d3().then(function(d3) {
            var margin = parseInt(attrs.margin) || 0;
            var barHeight = parseInt(attrs.barHeight) || 20;
            var barPadding = parseInt(attrs.barPadding) || 5;

            // Browser onresize event
            window.onresize = function() {
               scope.$apply();
            };

            // Watch for resize event
            scope.$watch(function() {
               return angular.element($window)[0].innerWidth;
            }, function() {
               scope.render(scope.data);
            });

            scope.$watch('data', function(newData) {
               scope.render(newData);
            }, true);

            scope.$on('display', function(active) {
               if (active)
                  scope.render(scope.data);
            });

            var svg = d3.select(element[0]).append('svg').style('width', '100%').append('g');

            // var div = d3.select(element[0])
            // .append('div')
            // .style('width', '100%');

            scope.render = function(data) {
               // remove all previous items before render
               svg.selectAll('*').remove();

               // If we don't pass any data, return out of the element
               if (!data)
                  return;

               // setup variables
               var width = d3.select(element[0]).node().offsetWidth - margin;

               // var width = 50;

               var doc = scope.doc;
               
               // calculate the height
               var height = doc.word.length * (1 + 32);

               // Use the category20() scale function for multicolor support
               var color = d3.scale.category20();

               // our xScale
               var xScale = d3.scale.linear().domain([0, d3.max(data, function(d) {
                  return d.score;
               })]).range([0, width]);

               // set the height based on the calculations above
               svg.attr('height', height);

               var wordNodes = doc.word.map(function(word) {
                  return {
                     name: word.form, children: [],
                  };
               })

               var nodes = wordNodes.map(function(word) {
                  return {
                     name: word.form, children: word.hasOwnProperty('dep') ? [wordNodes[word.dep.head - 1]] : [],
                  };
               })

               var force = d3.layout.force();

               var links = force.links(nodes);

               var link = svg.selectAll('.link').data(links).enter().append('path').attr('class', 'link');

               // create the rectangles for the bar chart
               var node = svg.selectAll('.node').data(nodes).enter().append('g').attr('class', 'node');

               node.append('circle').attr('r', 4.5);

               node.append('text').text(function(n) {
                  return n.name;
               });
               // .attr('x', width - 100)
               // .attr('y', function(word) {
               // return (1 + word.idx) * 32;
               // })
               // .attr('class', 'lead');
               force.start();
            }
         });
      }
   }
}]);

documentDirectives.directive('dagreDepTree', ['$window', '$timeout', 'd3Service', 'dagreD3Service', '_',
   function($window, $timeout, d3Service, dagreD3Service, _) {
      return {
         restrict: 'A',
         link: function(scope, element, attrs) {
            d3Service.d3().then(
            function(d3) {
               dagreD3Service.dagreD3().then(
                     function(dagreD3) {
                        scope.$on('display', function(active) {
                           if (active) {
                              scope.render();
                           }
                        });

                        function d(u, v) {
                           var dx = u.x - v.x;
                           var dy = u.y - v.y;
                           return Math.sqrt(dx * dx + dy * dy);
                        }

                        function sign(x) {
                           if (x < 0)
                              return -1;
                           else if (x > 0)
                              return 1;
                           else
                              return 0;
                        }

                        var layout = {
                           run: function(inputGraph) {
                              // console.log('>>', inputGraph);
                              var g = new dagreD3.Digraph();

                              inputGraph.eachNode(function(u, value) {
                                 if (value === undefined)
                                    value = {};
                                 g.addNode(u, { width: value.width, height: value.height });
                                 if (value.hasOwnProperty('rank')) {
                                    g.node(u).prefRank = value.rank;
                                 }
                              });

                              inputGraph.eachEdge(function(e, u, v, value) {
                                 if (value === undefined)
                                    value = {};
                                 var newValue = {
                                    e: e,
                                    minLen: value.minLen || 1,
                                    width: value.width || 0,
                                    height: value.height || 0,
                                    points: []
                                 };

                                 g.addEdge(null, u, v, newValue);
                              });

                              // Initial graph attributes
                              var graphValue = inputGraph.graph() || {};
                              g.graph({
                                 rankDir: graphValue.rankDir, 
                                 orderRestarts: graphValue.orderRestarts
                              });

                              g.eachNode(function(u, value) {
                                 value.x = 300; // + value.width / 2;
                                 value.y = (1 + u) * 45;
//                                 value.height = 20;
                                 // value.rx = value.height / 2;
                                 // value.ry = value.height / 2;
                              });
                              
                              g.eachEdge(function(e, u, v, value) {
                                 var uNode = g.node(u);
                                 var vNode = g.node(v);
                                 var span = v - u;
                                 var x = uNode.x - 15;
                                 
                                 // Set up info on the edge for later drawing
                                 var edge = g.edge(e);
                                 edge.span = Math.abs(span);
                                 
                                 value.points = [{
                                    x: x, 
//                                    y: uNode.y + sign(span) * Math.max(- uNode.height / 2, (uNode.height / 2 - 4 * Math.abs(span)))
                                    y: uNode.y 
                                 },
                                 {
                                    x: x - (30 + 40 * (Math.abs(span) - 1)), 
                                    y: uNode.y + (vNode.y - uNode.y) / 2
                                 }, 
                                 {
                                    x: x, 
//                                    y: vNode.y - sign(span) * Math.max(- vNode.height / 2, (vNode.height / 2 - 4 * Math.abs(span)))
                                    y: vNode.y
                                 }];
                              });

//                              var edges = _.sortBy(g.edges(), function(e) { return g.edge(e).span; });
//                              console.log(edges);
                              
                              return g;
                           }
                        }

                        var doc = scope.doc;
                        var lang = scope.language.key;

                        var svg = d3.select(element[0])
                           .append('svg')
                           .style('width', '100%')
                           .attr('height', (1 + doc.word.length) * 45)
                           .append('g');

                        scope.render = function() {
                           var g = new dagreD3.Digraph();

                           doc.word.forEach(function(word) {
                              g.addNode(word.idx, {
                                 label: word.form, rank: 'min'
                              });
                           });

                           doc.word.forEach(function(word) {
                              if (word.dep && word.dep.head > 0) {
//                                 console.log('word.dep:', word.dep);
                                 g.addEdge(null, word.idx, word.dep.head - 1, { label: word.dep.type });
                              }
                           });

                           var renderer = new dagreD3.Renderer();
                           renderer.edgeInterpolate('step');
                           renderer.layout(layout).run(g, svg);
                        }
                     });
            });
         }
      }
   }]);