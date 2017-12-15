/**
 * New node file
 */

var countWords = function(key, values) {
    return Array.sum(values);
}

var targetLemma = function() {
   var counts = {};
   this.lms.forEach(function (lm) {
      var words = [lm.source.lemma, lm.taget.lemma];
      for (var w in words) {
         if (! lm.ta in counts) {
      }
           counts[lm.target.lemma] = {};
           counts[lm.target.lemma].count = 1;
       }
       else
           counts[lm.target.lemma] += 1;
       
       
   });
   for (var w in counts)
       emit(w, counts[w]);
}

db.runCommand({
   mapReduce: 'docs',
   map: targetLemma,
   reduce: countWords,
   out: 'lemmas',
   query: { lms: { $exists: true } },
})
