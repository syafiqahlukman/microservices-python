**Stateful Set** 
- We make a stateful set because we want our cue to remain intact even if the Pod crashes or restarts 
- We want the messages within the queue to stay persistent until they've been pulled from the queue
- A stateful set is similar to a deployment in that it manages the deployment and scaling of a set of pods and these pods are based on an identical container spec 
- But unlike a deployment, with a stateful set, each pod has a persistent identifier like (web-01, web-02)that it maintains across any rescheduling 
- This means that if a pod fails, the persistent pod identifiers make it easier to match existing volumes to the new pods that replace any that have failed. The unique names make it easier to reconnect the saved data (volumes) to the new programs that replace the failed ones.
- There would be a master pod that is able to actually persist data to its physical storage (can write and read) and the rest of the pods would be slaves and they would only be able to read the data from their physical storage
- The physical storage that the slave pods use basically continuously syncs with the master pods physical storage because that's where all of the data persistence happens
- In our case, we are just going to use 1 replica (the master). For this particular queuing service, we are going to be persisting the data in our queues service because if our instance fails, we dont want to lose all of the messages that havent been processed because then when the users that uploaded those videos that produce those messages would never get a response back
- So basically we want to attach a piece of storage (volume) on our local to the container instance and if the container instance happens to die, of course the storage volume that was mounted would remain intact. Then, when a new pod redeployed it will once again have that same physical storage mounted to it

**Stateful Set vs. Deployment:**

- Similarities: Both manage how programs (pods) are started and scaled.
- Differences:
    - StatefulSet: Each program (pod) has a unique name (like web-01, web-02) that stays the same even if it restarts.
    - Deployment: Programs (pods) don't have unique names that persist across restarts

