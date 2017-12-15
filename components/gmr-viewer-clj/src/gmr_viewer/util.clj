(ns gmr-viewer.util
  (:require [noir.io :as io]
            [markdown.core :as md]))

(defn md->html
  "reads a markdown file from public/md and returns an HTML string"
  [filename]
  (md/md-to-html-string (io/slurp-resource filename)))

(defn map* [f xs]
  (lazy-seq
    (if (empty? xs)
      ()
      (cons (apply f (first xs))
            (map* f (rest xs))))))

