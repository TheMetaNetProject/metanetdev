function(doc) {        
  var newDoc = new Document();       
  
  var field = function(name, value, type) { 
     newDoc.add(value, {
        field: name, 
        store: 'yes',
        'type': type ? type : 'string'
     });        
  }        
  
  if ('lms' in doc) { 
    field('id', doc._id); 
    doc.lms.forEach(function(lm) {
      field('score', lm.score, 'double');
      
      // Source
      field('source-form', lm.source.form);   
      field('source-lemma', lm.source.lemma.toLowerCase());   
      lm.source.concepts.forEach(function(c) {
	field('source-concept', c);
      });
      lm.source.schemanames.forEach(function(s) {
	field('source-schema', s);
      });
  
      // Target
      field('target-form', lm.target.form);   
      field('target-lemma', lm.target.lemma.toLowerCase()); 
      field('target-concept', lm.target.concept); 
      field('target-schema', lm.target.schema); 
    }); 
    return newDoc;        
  }       
  return null;     
}
