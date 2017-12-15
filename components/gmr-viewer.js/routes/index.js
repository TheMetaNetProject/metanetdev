/*
 * GET home page.
 */

var mongoose = require('mongoose-paginate');
var document = require('../models/Document.js')

var connection = mongoose.createConnection('localhost', 'test');

var Documents = {};

var loadDocuments = function(err, names) {
   // console.log(names);
   Documents = {};
   
   var Schema = mongoose.Schema;
   var documentSchema = document.documentSchema;
   for (var i = 0; i < names.length; ++i) {
      var elems = names[i].name.split('.');
      if (elems[1].match(/^docs_/)) {
         var collName = elems.slice(1).join('.');
         var collElems = collName.split('_');
         var lang = collElems.slice(1).join('_')
         console.log('>> adding collection', lang, collName);
         Documents[lang] = connection.model(
               'Document_' + lang,
               new Schema(documentSchema, { collection: collName }));
      }
   }
}

connection.on('open', function(ref) {
   console.log('Connected to mongo server.');

   // Get collection names
   connection.db.collectionNames(loadDocuments);
   console.log('>> docs:', Object.keys(Documents));
});

exports.index = function(req, res) {
   res.render('index', {
      title: 'GMR Viewer'
   });
};

// JSON API for list of documents
exports.docs = function(req, res) {
   var callback = function(error, documents) {
      // console.log('>> documents', documents);
      res.json(documents);
   };

   console.log('>> req:', req.params, req.query);
    console.log('>> _id:', req.param('_id'));
   // console.log('>> file:', req.param('file'));
   // console.log('>> n:', req.param('n'));
   console.log('>> lang:', req.params.lang);

   console.log('>> search:', req.query.search);
   var search = JSON.parse(req.query.search);

   var _id = req.query._id;
   
   // console.log('>> search (JSON):', search);
//   var criteria = [{
//      lms: {
//         $exists: true
//      }
//   }];

   var criteria = [];
   
   if (search) {
      for (k in search) {
         console.log('k:', k);
         var f = 'lms.' + k.split('_').join('.')
         // console.log('f:', f);
         if (search[k]) {
            var c = new Object();
            // c[f] = new RegExp(search[k]);
            if (k != 'score')
               c[f] = search[k];
            else
               c[f] = {
                  $gt: parseFloat(search[k])
               }
            criteria.push(c);
         }
      }
      console.log(criteria);
   }

   if (req.query._id != '') {
      console.log('> _id:', _id);
      console.log('> up:', req.query.up);
      if (req.query.up == 'true') {
//         console.log('-- in gte', req.params.file.input, req.params.n.input);
         console.log('-- in gte', _id);
         criteria.push({ _id: { $gte: _id } });
      }
      else {
         console.log('-- in lte', _id);
         criteria.push({ _id: { $lte: _id } });
      }
      console.log('criteria:', criteria);
   }

   if (criteria.length == 0)
      criteria = {};
   else if (criteria.length > 1)
      criteria = { $and: criteria };
   else
      criteria = criteria[0];

   console.log('criteria:', criteria);

   var lang = req.params.lang.input;
   console.log('lang:', lang);
   Documents[lang]
      .find({
//         $query: criteria, $orderby: { file: 1, n: 1 }
         $query: criteria, $orderby: { _id: 1 }
         //, $maxScan: 5000
      })
      .limit(20)
      .exec(callback);
};

exports.languages = function(req, res) {
   res.json(Object.keys(Documents).map(function(lang) {
      switch (lang) {
      case 'en':
         return {
            key: lang, display: 'English'
         };
      case 'es':
         return {
            key: lang, display: 'Spanish'
         };
      case 'ru':
         return {
            key: lang, display: 'Russian'
         };
      case 'fa':
         return {
            key: lang, display: 'Farsi'
         };
      default:
         return {
            key: lang, display: lang
         };
      }
   }));
};

// JSON API for getting a single document
exports.doc = function(req, res) {
   // console.log('> in exports.doc, %s', req.params.docId);

   var docId = req.params.docId;
   Document.find({
      id: docId
   }, '', {
      lean: true
   }, function(err, doc) {
      if (doc) {
         res.json(doc[0]);
         // console.log('>> doc', doc);
      }
      else {
         res.json({
            error: true
         });
      }
   });
};
