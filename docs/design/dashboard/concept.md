# Problem statement

I want to create simple UI that will allow me to better analyze experiment results
and compare them between each other, as the current way of doing this (CLI + manual "eye based")
is simply miserable.

# User stories

I want to be able to...

1. see the available experiment batch results in a list form (just names of batches),
2. see the basic info for each experiment batch (by clicking on it or sth, solver description, timestamps),
3. have possibility to see analyze results for given batch,
4. have possibility to see analyze results for given experiment from given batch,
5. have possibility to compare two experiment batches side by side, this comparision should be on both bach & individual experiment level
6. have possibility to compare performance of two batches
7. see performance results for all available batch results (side by side for every single experiment + some summary)

# Implementation concept

As it seems that some data processing is required I wouldn't start with React app only. Actually I would start
with client-server architecture.

Client - React application utilizing React Router for diffrent tabs. Responsible for some final data processing, styling
and presenting it to the user.

Server - Rust (just to keep it simple and not introduce new technology) application utilising tokio + tower or some other web framework.
Responsible for serving data to client, extracting information from file system (*), running ecdk when needed for analysis purposes.
Server should be able to make use of already computed & processed results.

(*) Currently all information & results reside directly in file system, however there is a plan to migrate it to sqlite.

# Client

Use React Router; only few routes are required.

Home page should display list of available experiment results with some basic information (1).
Maybe just present each experiment as <summary> & <details> markers, with description in details (2).

There should be links to see the analyze results of given experiment (button / link next to summary text of given batch) (3, 4).

There should be possibility to go to the preformance analysis page (6).

Required information (endpoints):

1. Experiment batch names alongside it's basic metadata, experiment names, timings, global stats
2. Analyze result for each experiment batch
3. Analyze result for each experiment of a batch (images as urls)

# Server 

Exposing the above endpoitns.

Taking two main parameters: `raw-data-dir`, `processed-data-dir`, and some auxilary such as port etc.

# Communication Client <-> Server

HTTP & Json should be enough. In case of performance problems I can consider moving to gRPC.


# Client in more details

There should be header enabling navigation between different pages.

## Home page

List of experiment batches names. Each batch name is an `<summary>` element.



