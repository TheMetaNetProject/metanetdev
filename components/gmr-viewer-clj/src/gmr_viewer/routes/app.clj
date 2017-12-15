(ns gmr-viewer.routes.app
  (:require [com.ashafa.clutch :as clutch]
            [clojure.string :refer [join split]]
            [gmr-viewer.util :refer [map*]]
            [compojure.core :refer [defroutes context GET PUT ANY POST]]
            [cheshire.core :refer [encode decode generate-string parse-string]]
            [templates.index :refer [index]]
            [clojure.pprint :as pprint]
            [clojurewerkz.elastisch.rest          :as esr]
            [clojurewerkz.elastisch.rest.document :as esd]
            [clojurewerkz.elastisch.query         :as q]))

;; All the dbs this application uses are like the following.
(def prefix #"test_docs")

(defn get-db [coll]
  (clutch/couch (join "_" [prefix coll])))

(defn all-documents [coll]
  (get-db coll))

(defn range-documents [coll start-id count]
  (clutch/all-documents 
    (get-db coll) 
    (let [params {:limit count :include_docs true}]
      (if (not= start-id "")
        (assoc params :startkey start-id)
        params))))

(defn normalize [doc]
  (assoc doc :lms (get doc :lms [])))

(defn describe-collection [coll]
  {:key coll
   :display (get {:en "English" 
                  :es "Spanish" 
                  :ru "Russian" 
                  :fa "Farsi"} 
                 (keyword coll) coll)})
    
(defn all-collections []
  (map #(describe-collection ((split % #"_" 3) 2)) 
       (filter #(re-find prefix %) (clutch/all-databases))))

(defn get-document [coll id]
  (get (get-db coll) id))

(defn get-documents [coll ids]
  (clutch/all-documents (get-db coll) {:include_docs true} {:keys ids}))

(defn hello [s]
  (format "Hello there %s, how are you?" s))

(defn json-response [data & [status]]
  {:status (or status 200)
   :headers {"Content-Type" "application/json"}
   :body (generate-string data)})

(defn uniq [xs]
  (reduce #(if (= %2 (last %1)) %1 (conj %1 %2)) [] xs))

(defn search-lms [coll size start-id params]
  (let [lms  (esd/search (esr/connect) "lms-test2" "lms2"
                         :size size
                         :query (:query params {:range {:id {:gte start-id}}}) 
                         :filter (:filter params {:match_all {}})
                         :_source (:_source params false)
                         :sort [{:id {:order :asc}}])
        
        ks   [:_id :_rev :id :n :file :text :word :lms]
        docs (map #(select-keys (:doc %) ks)
                  (get-documents coll (sort (set (map :_id (get-in lms [:hits :hits]))))))]
    (println "search-lms:" coll size start-id (:query params))
  {:docs docs :lms lms}))

(defroutes app-routes
  (GET "/" [] (index "GMR Viewer"))
;  (POST "/test" r (json-response {:reply (parse-string (slurp (:params r)))}))
  (POST "/test" request (json-response [{:reply (:params request)}]))
  (GET "/collections" []     (json-response (all-collections)))
  (GET "/hello/:name" [name] (hello name))
  (context "/docs/:coll" [coll]
           (GET "/all/:count" [count] 
                (->> coll all-documents (take (Integer/parseInt count))))
           (GET "/page/:size/:start-id" [size start-id] 
                (range-documents coll start-id size))
           (POST "/page/:size/:start-id" [size start-id]
                 (fn [request] 
                   (json-response (search-lms coll size start-id (:params request))))) 
           (GET "/doc/:id" [id] 
                (json-response (get-document coll id)))))
