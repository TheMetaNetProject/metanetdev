(ns indices.es
  (:require [cheshire.core :refer [encode decode]]
            [clojure.java.io :as io]))

(defn lms-index [env]
  (let [doc (get env "doc")
        lms (get doc "lms")
        fields (fn [lm] 
                 (:source-lemma   (get-in lm ("source" "lemma")))
                 (:source-form    (get-in lm ("source" "form")))
                 (:source-schema  (get-in lm ("source" "schemanames")))
                 (:source-concept (get-in lm ("source" "concepts")))
                 (:target-lemma   (get-in lm ("target" "lemma")))
                 (:target-form    (get-in lm ("target" "form")))
                 (:target-schema  (get-in lm ("target" "schemaname")))
                 (:target-concept (get-in lm ("target" "concept"))))]
    (swap! env (if (> 0 (count lms))
                 (map fields lms) 
                 {:_ignore true}))))

(defn make-index [db name type script script-lang]
  {:type "couchdb"
   :couchdb {:host "localhost"
             :port 5984
             :db db
             :filter nil
             :script script
             :script_type script-lang}
   :index {:index name
           :type type
           :bulk_size "10000"
           :bulk_timeout "10000ms"}})

