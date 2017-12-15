(defproject gmr-viewer "0.1.2-SNAPSHOT"
  :description "A Viewer for the GMR database."
  :url "http://192.168.4.172:4000"
  :dependencies [[org.clojure/clojure "1.6.0"]
                 [lib-noir "0.9.4"]
                 [ring-server "0.3.1"]
                 [selmer "0.7.1"]
                 [com.taoensso/timbre "3.3.1"]
                 [com.taoensso/tower "3.0.2"]
                 [markdown-clj "0.9.54"]
                 [environ "1.0.0"]
                 [im.chit/cronj "1.4.2"]
                 [noir-exception "0.2.2"]
                 [prone "0.6.0"]
                 [com.ashafa/clutch "0.4.0"]
                 [org.clojure/clojurescript "0.0-2371"]
                 [hiccup "1.0.5"]
                 [cheshire "5.3.1"]
                 [clj-jade "0.1.5"]
                 [ring.middleware.logger "0.5.0"]
                 [clojurewerkz/elastisch "2.1.0-beta9"]]
  :bower {:directory "resources/public/js/lib"}
  :bower-dependencies [[angular "~1.2.x"]
                       [angular-mocks "~1.2.x"]
                       [bootstrap "~3.3.1"]
                       [angular-route "~1.2.x"]
                       [angular-resource "~1.2.x"]
;                       [angular-animate "~1.2.x"]
                       [jquery "~2.1.1"]
                       [lodash "~2.4.1"]
                       [d3 "~3.4.11"]
                       [angular-busy "~4.0.x"]]
  :repl-options {:init-ns gmr-viewer.repl}
  :jvm-opts ["-server"]
  :plugins [[lein-ring "0.8.12"]
            [lein-environ "0.5.0"]
            [lein-ancient "0.5.5"]
            [lein-npm "0.4.0"]
            [lein-bower "0.5.1"]]
  :ring {:handler gmr-viewer.handler/app
         :init    gmr-viewer.handler/init
         :destroy gmr-viewer.handler/destroy}
  :profiles {:uberjar {:aot :all}
             :production {:ring {:open-browser? false
                                 :stacktraces?  false
                                 :auto-reload?  false}}
             :dev {:ring {:open-browser? false
                          :stacktraces?  true
                          :auto-reload?  true}
                    :dependencies [[ring-mock "0.1.5"]
                                   [ring/ring-devel "1.3.1"]
                                   [pjstadig/humane-test-output "0.6.0"]
                                   [com.cemerick/austin "0.1.5"]]
                    :injections [(require 'pjstadig.humane-test-output)
                                 (pjstadig.humane-test-output/activate!)]
                    :env {:dev true}
                    :plugins [[com.cemerick/austin "0.1.5"]]}}
  :min-lein-version "2.0.0")
