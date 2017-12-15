/**
 * Module dependencies.
 */

var express = require('express');
var http = require('http');
var path = require('path');

var app = express();

// all environments
app.set('port', process.env.PORT || 3000);
app.set('views', __dirname + '/views');
app.set('view engine', 'jade');
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.json());
app.use(express.urlencoded());
app.use(express.methodOverride());
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));
app.use('/components', express.static(path.join(__dirname, '/bower_components')));

// development only
if ('development' === app.get('env')) {
   app.use(express.errorHandler());
}

var routes = require('./routes');
var user = require('./routes/user');

app.param(function(name, fn) {
   if (fn instanceof RegExp) {
      return function(req, res, next, val) {
         var captures;
         if (captures = fn.exec(String(val))) {
            req.params[name] = captures;
            next();
         }
         else {
            next('route');
         }
      };
   }
});

//
app.param('file', /[^/]*/);
app.param('n', /\d*/);
app.param('_id', /[^/]*/);
app.param('lang', /en|es|fa|ru|[\w.]+/);

//app.get('/docs/docs/:lang/:_id', routes.docs);
app.get('/docs/docs/:lang', routes.docs);
app.get('/docs/languages', routes.languages);
app.get('/docs/:docId', routes.doc);
app.get('/', routes.index);
// app.post('/docs', routes.create);

app.get('/users', user.list);

http.createServer(app).listen(app.get('port'), function() {
   console.log('Express server listening on port ' + app.get('port'));
});
