(def open-for-business? (atom true))
(def haircut-count (agent 0))
(def waiting-room (ref []))
(def waiting-room-size 3)

(defn open-shop [duration]
  (do (Thread/sleep duration) (swap! open-for-business? not)))
 
(defn add-customers []
  (future
    (while @open-for-business?
      (println "Waiting Room:" @waiting-room)
      (dosync
        (if 
          (< (count (ensure waiting-room)) waiting-room-size)
          (alter waiting-room conj :customer)))
        (Thread/sleep (+ 10 (rand-int 21))))))
 
(defn get-next-customer []
  (dosync
    (let [next-customer (first (ensure waiting-room))]
      (when next-customer (alter waiting-room rest) next-customer))))
 
(defn cut-hair []
  (future
    (while @open-for-business?
      (when-let [next-customer (get-next-customer)]
        (Thread/sleep 20)
        ;; do we want to continue cut hair before (!)
        ;; the actual value is set (possibly) ???
        (send haircut-count inc)))))
 
(do 
  (cut-hair)
  (add-customers)
 
  (println "Open barber shop for 10 secs")
  (open-shop 10000)
 
  (println "Number of cuts:" @haircut-count)
  (System/exit 0))