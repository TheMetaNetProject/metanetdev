(ns templates.index
  (:require [hiccup.core :as html]
            [hiccup.page :as page]))

(def ^:dynamic *public*
  "/public")

(defn- with-path [prefix & others]
  (apply str (list* *public* prefix others)))
            
;; -- bower-components-start --
(def bower-components
  ["/lodash/dist/lodash.js"
   "/jquery/dist/jquery.min.js"
   "/angular/angular.js"
   "/angular-route/angular-route.js"
   "/angular-resource/angular-resource.js"
   "/d3/d3.min.js"
   "/angular-busy/dist/angular-busy.js"])
;; -- bower-components-end --

(def components
  (map #(with-path "/js/lib" %) bower-components))

(def js
  (map #(with-path "/js" %)
       ["/dagre-d3.js"
        "/app.js"
        "/controllers.js"    
        "/services.js"  
        "/directives.js"]))

(defn- head [title]
  [:head
   [:title title]
   [:meta {:charset 'utf-8}]
   [:meta {:name 'viewport :content "width=device-width, initial-scale=1, user-scalable=no"}]
   [:link {:rel "stylesheet" :href (with-path "/css" "/style.css")}]
   [:link {:rel "stylesheet" :href (with-path "/js/lib" "/bootstrap/dist/css/bootstrap.min.css")}]    
   [:link {:rel "stylesheet" :href (with-path "/js/lib" "/angular-busy/dist/angular-busy.css")}]
   (for [s (concat components js)]
     [:script {:src s}])])

(defn- body [title]
  [:body
   [:nav.navbar.navbar-inverse.navbar-fixed-top {:role 'navigation}
    [:div.navbar-header
     [:a.navbar-brand {:href "#/docs"} title]]] 
   [:div.container
    [:ng-view.container-fluid]]])

(defn index [title]
  (page/html5 
    {:ng-app 'gmrViewerApp :lang 'en}
    (head title)
    (body title)))


