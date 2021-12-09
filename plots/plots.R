library(ggplot2)
library(readr)
library(magrittr)
library(dplyr)

no_failures <- readr::read_csv("benchmarks_remote/no_failure.csv")
failure <- readr::read_csv("benchmarks_remote/results_leader_failure.csv")

leader_failure_2 <- readr::read_csv("benchmarks_remote/leader_failure_2_clusters.csv")
no_failure_2 <- readr::read_csv("benchmarks_remote/no_failure_2_clusters.csv")

txn_leader_failure_2 <- readr::read_csv("benchmarks_remote/with_txn_leader_failure_2_clusters.csv")
txn_no_failure_2 <- readr::read_csv("benchmarks_remote/with_txn_no_failure_2_clusters.csv")

get_operations_from_df <- function(df){
  df <- dplyr::arrange(df, time)
  start <- df$time[1]
  
  df$time <- df$time - start
  
  df %>% 
    dplyr::mutate(dummy_cmd = ifelse(command %in% c("get", "set"), 1, 0)) %>% 
    dplyr::mutate(cum_operations = cumsum(dummy_cmd))
}

get_first_failure <- function(df){
  dplyr::filter(df, command == "err") %>% 
    dplyr::slice_head(n=1) %>% 
    dplyr::pull(time)
}

no_failures <- get_operations_from_df(no_failures)
failure <- get_operations_from_df(failure)

no_failure_2 <- get_operations_from_df(no_failure_2)
leader_failure_2 <- get_operations_from_df(leader_failure_2)

txn_leader_failure_2 <- get_operations_from_df(txn_leader_failure_2)
txn_no_failure_2 <- get_operations_from_df(txn_no_failure_2)

generate_cum_requests_plot <- function(df1, desc1, df2, desc2, title, legend=TRUE){
  first_failure <- get_first_failure(df1)
  if (length(first_failure) == 0){
    first_failure <- get_first_failure(df2)
  }
  
  plot_res <- ggplot() +
    geom_line(data = df1, aes(time, cum_operations, color = "blue")) +
    geom_line(data = df2, aes(time, cum_operations, color = "red")) +
    geom_vline(xintercept=c(first_failure), linetype="dotted") +
    ggtitle(title) +
    ylab("Cumulative Requests") +
    xlab("Time (seconds)") +
    scale_colour_manual(name = 'Legend', 
                        values =c('red'='red','blue'='blue'),
                        labels = c(desc1, desc2))
  
  if (legend){
    plot_res <- plot_res +
      theme(
        legend.position = c(.95, .05),
        legend.justification = c("right", "bottom"),
        legend.box.just = "right",
        legend.margin = margin(6, 6, 6, 6)
      ) 
  }
  
  plot_res
}

get_operations_by_second <- function(df){
  df %>% 
    dplyr::mutate(seconds = floor(time)) %>% 
    dplyr::group_by(seconds) %>% 
    dplyr::summarise(operations = sum(dummy_cmd))
}

generate_requests_per_second_plot <- function(no_failure_df, failure_df, title, legend=TRUE){
  first_failure <- get_first_failure(failure_df)
  
  plot_res <- ggplot() +
    geom_line(data = get_operations_by_second(failure), 
              aes(seconds, operations, color = "red")) +
    geom_line(data = get_operations_by_second(no_failure_df), 
              aes(seconds, operations, color = "blue")) +
    geom_vline(xintercept=c(first_failure), linetype="dotted") +
    ggtitle(title) +
    ylab("Requests per second") +
    xlab("Time (seconds)") +
    scale_colour_manual(name = 'Legend', 
                        values =c('red'='red','blue'='blue'),
                        labels = c('No Failure','Failure (at dotted line)'))
  
  if (legend){
    plot_res <- plot_res +
      theme(
        legend.position = c(.95, .05),
        legend.justification = c("right", "bottom"),
        legend.box.just = "right",
        legend.margin = margin(6, 6, 6, 6)
      ) 
  }
  
  plot_res
}

p1 <- generate_cum_requests_plot(no_failures, "No Failure",
                           failure, "Failure (at dotted line)", 
                           "Single Cluster", FALSE)
p2 <- generate_cum_requests_plot(no_failure_2, "No Failure",
                           leader_failure_2, "Failure (at dotted line)", 
                           "Two Clusters", FALSE)
p3 <- generate_cum_requests_plot(txn_no_failure_2, "No Failure",
                                 txn_leader_failure_2, "Failure (at dotted line)",
                                 "Two Clusters (with txn)")

cum_requests_plot <- cowplot::plot_grid(p1, p2)

p3

p1 <- generate_requests_per_second_plot(no_failures, failure, "Single Cluster")
p2 <- generate_requests_per_second_plot(no_failure_2, leader_failure_2, "Two Clusters")
p3 <- generate_requests_per_second_plot(txn_no_failure_2, txn_leader_failure_2, "Two Clusters (with txn)")

requests_per_sec_plot <- cowplot::plot_grid(p1, p2)




