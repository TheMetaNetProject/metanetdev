(ns gmr-viewer.handler
  (:require [compojure.core :refer [defroutes context GET]]
            [gmr-viewer.routes.home :refer [home-routes]]
            [gmr-viewer.routes.app :refer [app-routes]]
            [gmr-viewer.middleware :refer [load-middleware]]
            [gmr-viewer.session-manager :as session-manager]
            [noir.response :refer [redirect]]
            [noir.util.middleware :refer [app-handler]]
            [ring.middleware.defaults :refer [site-defaults]]
            [compojure.route :as route]
            [taoensso.timbre :as timbre]
            [taoensso.timbre.appenders.rotor :as rotor]
            [selmer.parser :as parser]
            [environ.core :refer [env]]
            [cronj.core :as cronj]))

(defn init
  "init will be called once when
			   app is deployed as a servlet on
			   an app server such as Tomcat
			   put any initialization code here"
  []
  (timbre/set-config!
    [:appenders :rotor]
    {:min-level :debug
     :enabled? true
     :async? false ; should be always false for rotor
     :max-message-per-msecs nil
     :fn rotor/appender-fn})
  
  (timbre/set-config!
    [:shared-appender-config :rotor]
    {:path "log/gmr_viewer.log" :max-size (* 512 1024) :backlog 10})
  
  (if (env :dev) (parser/cache-off!))
  ;; start the expired session cleanup job
  (cronj/start! session-manager/cleanup-job)
  (timbre/info "\n-=[ gmr-viewer started successfully"
               (when (env :dev) "using the development profile") "]=-"))

(defn destroy
  "destroy will be called when your application
			   shuts down, put any clean up code here"
  []
  (timbre/info "gmr-viewer is shutting down...")
  (cronj/shutdown! session-manager/cleanup-job)
  (timbre/info "shutdown complete!"))

;; timeout sessions after 30 minutes
(def session-defaults
  {:timeout (* 60 30)
   :timeout-response (redirect "/")})

(defn- mk-defaults
  "set to true to enable XSS protection"
  [xss-protection?]
  (-> site-defaults
    (update-in [:session] merge session-defaults)
    (assoc-in [:security :xss-protection :enable?] xss-protection?)
    (assoc-in [:security :anti-forgery] xss-protection?)))

(defroutes base-routes
  (route/resources "/")
  (route/not-found "Not Found"))

(def app 
  (app-handler
    ;; add your application routes here
    [app-routes home-routes base-routes]
    ;; add custom middleware here
    :middleware (load-middleware)
    :ring-defaults (mk-defaults false)
    ;; add access rules here
    :access-rules []
    ;; serialize/deserialize the following data formats
    ;; available formats:
    ;; :json :json-kw :yaml :yaml-kw :edn :yaml-in-html
    :formats [:json-kw :edn :transit-json]))
