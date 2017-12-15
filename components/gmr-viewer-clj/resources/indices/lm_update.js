/**
 * Update the lms key in a GMR sentence subdocument. 
 * This should go in a design document, under the "updates" key.
 */

 function (doc, req) {
    var lms = JSON.parse(req.body);
    doc.lms = lms; 
    return [doc, toJSON(lms)];
}