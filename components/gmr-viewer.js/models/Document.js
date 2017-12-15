// The model.

var mongoose = require('mongoose');
var Schema = mongoose.Schema;
var ObjectId = Schema.Types.ObjectId;
var Mixed = Schema.Types.Mixed;

mongoose.Model.paginate = function(query, resultsPerPage, callback, options) {
   var model = this;
   var options = options || {};
   var columns = options.columns || null;
   var sortBy = options.sortBy || {
      id: 1
   };
   var populate = options.populate || null;
   callback = callback || function() {};

   if (columns == null) {
      var query = model.find(query).limit(resultsPerPage).sort(sortBy);
   }
   else {
      var query = model.find(query).select(options.columns).limit(resultsPerPage).sort(sortBy);
   }
   if (populate) {
      query = query.populate(populate);
   }
   query.exec(function(error, results) {
      if (error) {
         callback(error);
      }
      else {
         model.count(query, function(error, count) {
            if (error) {
               callback(error);
            }
            else {
               callback(null, Math.ceil(count / resultsPerPage) || 1, results, count);
            }
            ;
         });
      }
      ;
   });
};

var docSchema = {
//   _id: ObjectId,
   _id: String,
   id: String,
   idx: Number,
   text: String,
   mtext: String,
   ctext: String,
   pn2imap: Mixed,
   p2imap: Mixed,
   word: [{
      n: Number,
      idx: Number,
      start: Number,
      end: Number,
      pos: String,
      rpos: String,
      form: String,
      lem: String,
      rlem: String,
      dep: {
         head: String,
         type: { type: String },
         subtype: String
      }
   }],
//   dparse: [{
//      n: Number,
//      idx: Number,
//      start: Number,
//      end: Number,
//      form: String,
//      lem: String,
//      pos: String,
//      dep: {
//         head: Number,
//         type: String
//      }
//   }],
   CMS: {
      idxset: [Number], targetlist: [{
         start: Number, end: Number, form: String, lemma: String, mword: String, wdomain: String,
         // schema: String,
         idxlist: [Number]
      }]
   },
   mwelist: [Number],
   lms: [{
      extractor: String,
      name: String,
      source: {
         start: Number,
         end: Number,
         form: String,
         lemma: String,
         lpos: String,
         schemas: [String],
         concept: String,
         concepts: [String]
      },
      seed: String,
      score: Number,
      cms: [String],
      target: {
         start: Number,
         end: Number,
         form: String,
         lemma: String,
         mword: String,
         wdomain: String,
         concept: String,
         idxlist: [Number]
      // schema: String,
      }
   }],
   lang: String
};

// var documentSchema = new Schema(, {
// collection: 'docs_en',
// toJSON: { virtuals: false }
// });
var parseMText = function() {
   var parsed = [];
   if (this.mtext) {
      var elements = this.mtext.split(' ');
      for (var i = 0; i < elements.length; ++i) {
         var ff = elements[i].split('=');
         parsed[i] = {
            word: ff[0], lemma: ff[1], pos: ff[2], idx: ff[3]
         };
      }
   }
   return parsed;
}

var documentSchemas = {};

var languages = ['en', 'fa', 'es', 'ru'];
for (var i = 0; i < languages.length; ++i) {
   var lang = languages[i];
   documentSchemas[lang] = new Schema(docSchema, { collection: 'docs_' + lang });
   documentSchemas[lang].virtual('mtext_parsed').get(parseMText);
}

exports.documentSchema = docSchema;
exports.documentSchemas = documentSchemas;
exports.languages = languages
