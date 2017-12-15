# =====================================================================
# Elasticsearch
# ---------------------------------------------------------------------
# Make index for 'lms' key; no index if no lms key is present
# ---------------------------------------------------------------------

def make_index(ctx):
    doc = ctx['doc']
    if 'lms' in doc:
        newDoc = dict()
        lms = doc['lms']
#         newDoc['id'] = doc['_id'].replace(':', '_')
#         Setup id as unanalyzed:
#         PUT /lms-index/_mapping/lm
#         {
#           "properties" : {
#             "id" : {
#               "type" :    "string",
#               "index": "not_analyzed"
#               
#             }
#           }
#         }
        newDoc['id'] = doc['_id']
        if 'perspective' in doc:
            newDoc['perspective'] = doc['perspective']
            
        for lm in doc['lms']:
            newDoc['score'] = lm['score']

            # Source
            source = lm['source']
            newDoc['source-form']           = source['form']
            newDoc['source-lemma']          = source['lemma']
            newDoc['source-concepts']       = source['concepts']
            newDoc['source-schemanames']    = source['schemanames']
            newDoc['source-schemafamilies'] = source['schemafamilies']

            # Target
            target = lm['target']
            newDoc['target-form']           = target['form']
            newDoc['target-lemma']          = target['lemma']
            newDoc['target-concept']        = target['concept']
            newDoc['target-schemaname']     = target['schemaname']
            newDoc['target-congroup']       = target['congroup']
            newDoc['target-schemafamily']   = target['schemafamily']
        return newDoc
    else:
        return None

lms = make_index(ctx)
if lms != None:
    ctx['doc'] = lms
else:
    ctx['ignore'] = True

