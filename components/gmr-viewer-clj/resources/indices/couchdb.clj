(ns couchdb.load
  (:require [com.ashafa.clutch :as clutch]
            [clojure.java.io :as io]
            [clojure.pprint :as pprint]))

(defn save-updates
  "Create or update a design document containing views used for database queries."
  [db & args]
  (apply clutch/save-design-document db :updates args))

(defn save-index
  "Create or update a design document containing views used for database queries."
  [db & args]
  (apply clutch/save-design-document db :index args))


;(defn update-design-document [db name keys code]
;  (clutch/save-design-document 
;    db "index" 
;    [:javascript {:by-lm {:index code}}]))

(defn -main []
  (do
    (save-updates "test_docs_en" "lms" 
                  [:javascript {:in-place 
                                (slurp (io/resource "indices/lm_update.js"))}])))