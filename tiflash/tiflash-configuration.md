---
title: TiFlash 配置参数
aliases: ['/docs-cn/dev/tiflash/tiflash-configuration/','/docs-cn/dev/reference/tiflash/configuration/']
summary: TiFlash 配置参数包括 PD 调度参数和 TiFlash 配置参数。PD 调度参数可通过 pd-ctl 调整，包括 replica-schedule-limit 和 store-balance-rate。TiFlash 配置参数包括 tiflash.toml 和 tiflash-learner.toml，用于配置 TiFlash TCP/HTTP 服务的监听和存储路径。另外，通过拓扑 label 进行副本调度和多盘部署也是可行的。
---

# TiFlash 配置参数

本文介绍了与部署使用 TiFlash 相关的配置参数。

## PD 调度参数

可通过 [pd-ctl](/pd-control.md) 调整参数。如果你使用 TiUP 部署，可以用 `tiup ctl:v<CLUSTER_VERSION> pd` 代替 `pd-ctl -u <pd_ip:pd_port>` 命令。

- [`replica-schedule-limit`](/pd-configuration-file.md#replica-schedule-limit)：用来控制 replica 相关 operator 的产生速度（涉及到下线、补副本的操作都与该参数有关）

  > **注意：**
  >
  > 不要超过 `region-schedule-limit`，否则会影响正常 TiKV 之间的 Region 调度。

- `store-balance-rate`：用于限制每个 TiKV store 或 TiFlash store 的 Region 调度速度。注意这个参数只对新加入集群的 store 有效，如果想立刻生效请用下面的方式。

  > **注意：**
  >
  > 4.0.2 版本之后（包括 4.0.2 版本）废弃了 `store-balance-rate` 参数且 `store limit` 命令有部分变化。该命令变化的细节请参考 [store-limit 文档](/configure-store-limit.md)。

    - 使用 `pd-ctl -u <pd_ip:pd_port> store limit <store_id> <value>` 命令单独设置某个 store 的 Region 调度速度。（`store_id` 可通过 `pd-ctl -u <pd_ip:pd_port> store` 命令获得）如果没有单独设置，则继承 `store-balance-rate` 的设置。你也可以使用 `pd-ctl -u <pd_ip:pd_port> store limit` 命令查看当前设置值。

- [`replication.location-labels`](/pd-configuration-file.md#location-labels)：用来表示 TiKV 实例的拓扑关系，其中 key 的顺序代表了不同标签的层次关系。在 TiFlash 开启的情况下需要使用 [`pd-ctl config placement-rules`](/pd-control.md#config-show--set-option-value--placement-rules) 来设置默认值，详细可参考 [geo-distributed-deployment-topology](/geo-distributed-deployment-topology.md)。

## TiFlash 配置参数

> **Tip:**
>
> 如果你需要调整配置项的值，请参考[修改配置参数](/maintain-tidb-using-tiup.md#修改配置参数)进行操作。

### 配置文件 tiflash.toml

#### listen_host

- TiFlash TCP/HTTP 等辅助服务的监听 host。建议配置成 0.0.0.0，即监听本机所有 IP 地址。
- 默认值：0.0.0.0

#### mark_cache_size

- TiFlash TCP 服务的端口。TCP 服务为内部测试接口，默认使用 9000 端口。在 TiFlash v7.1.0 之前的版本中，该端口默认开启，但存在安全风险。为了提高安全性，建议对该端口进行访问控制，只允许白名单 IP 访问。从 TiFlash v7.1.0 起，可以通过注释掉该端口的配置避免安全风险。当 TiFlash 配置文件未声明该端口时，该端口也不会开启。 建议在任何 TiFlash 的部署中都不配置该端口。(注: 从 TiFlash v7.1.0 起，由 TiUP >= v1.12.5 或 TiDB Operator >= v1.5.0 部署的 TiFlash 默认为安全版本，即默认未开启该端口) tcp_port = 9000 数据块元信息的内存 cache 大小限制，通常不需要修改
- 默认值：1073741824

#### minmax_index_cache_size

- 数据块 min-max 索引的内存 cache 大小限制，通常不需要修改
- 默认值：1073741824

#### delta_index_cache_size

- DeltaIndex 内存 cache 大小限制，默认为 0，代表没有限制
- 默认值：0

#### storage

##### main

###### dir

- 用于存储主要的数据，该目录列表中的数据占总数据的 90% 以上。
- 默认值：['/tidb-data/tiflash-9000']

##### latest

##### io_rate_limit

#### flash

##### service_addr

- 描述：TiFlash coprocessor 服务监听地址
- 默认值：0.0.0.0:3930

##### proxy

###### addr

- 描述：proxy 监听地址，不填则默认是 127.0.0.1:20170
- 默认值：127.0.0.1:20170

###### advertise-addr

- 描述：外部访问 addr 的地址，不填则默认使用 "addr" 的值 当集群部署在多个节点时，需要保证 `advertise-addr` 的地址可以从其他节点连接
- 默认值：

###### status-addr

- 描述：拉取 proxy metrics 或 status 信息的监听地址，不填则默认是 127.0.0.1:20292
- 默认值：127.0.0.1:20292

###### advertise-status-addr

- 描述：外部访问 status-addr 的地址，不填则默认使用 "status-addr" 的值 当集群部署在多个节点时，需要保证 `advertise-addr` 的地址可以从其他节点连接
- 默认值：

###### engine-addr

- 描述：外部访问 TiFlash coprocessor 服务的地址
- 默认值：10.0.1.20:3930

###### data-dir

- 描述：proxy 数据存储路径
- 默认值：/tidb-data/tiflash-9000/flash

###### config

- 描述：proxy 配置文件路径
- 默认值：/tidb-deploy/tiflash-9000/conf/tiflash-learner.toml

###### log-file

- 描述：proxy log 路径
- 默认值：/tidb-deploy/tiflash-9000/log/tiflash_tikv.log

#### logger

##### level

- 描述：log 级别（支持 "trace"、"debug"、"info"、"warn"、"error"），默认是 "info"
- 默认值：info

##### log

- 描述：proxy log 路径
- 默认值：/tidb-deploy/tiflash-9000/log/tiflash.log

##### errorlog

- 描述：TiFlash 错误日志。对于 "warn"、"error" 级别的日志，会额外输出到该日志文件中。
- 默认值：/tidb-deploy/tiflash-9000/log/tiflash_error.log

##### size

- 描述：单个日志文件的大小，默认是 "100M"
- 默认值：100M

##### count

- 描述：最多保留日志文件个数，默认是 10。对于 TiFlash 日志和 TiFlash 错误日志各自最多保留 `count` 个日志文件。
- 默认值：10

#### raft

##### pd_addr

- 描述：PD 服务地址. 多个地址以逗号隔开
- 默认值：10.0.1.11:2379,10.0.1.12:2379,10.0.1.13:2379

#### status

##### metrics_port

- 描述：Prometheus 拉取 metrics 信息的端口，默认是 8234
- 默认值：8234

#### profiles

##### default

###### max_threads

- 描述：`max_threads` 指的是执行一个 MMP Task 的内部线程并发度，默认值为 0。当值为 0 时，TiFlash 执行 MMP Task 的线程并发度为 CPU 核数。 该参数只有在系统变量 `tidb_max_tiflash_threads` 设置为 -1 时才会生效。
- 默认值：0

###### max_memory_usage

- 描述：单次查询过程中，节点对中间数据的内存限制 设置为整数时，单位为 byte，比如 34359738368 表示 32 GiB 的内存限制，0 表示无限制 设置为 [0.0, 1.0) 之间的浮点数时，指节点总内存的比值，比如 0.8 表示总内存的 80%，0.0 表示无限制 默认值为 0，表示不限制 当查询试图申请超过限制的内存时，查询终止执行并且报错
- 默认值：0

###### max_memory_usage_for_all_queries

- 描述：所有查询过程中，节点对中间数据的内存限制 设置为整数时，单位为 byte，比如 34359738368 表示 32 GiB 的内存限制，0 表示无限制 设置为 [0.0, 1.0) 之间的浮点数时，指节点总内存的比值，比如 0.8 表示总内存的 80%，0.0 表示无限制 默认值为 0.8，表示总内存的 80% 当查询试图申请超过限制的内存时，查询终止执行并且报错
- 默认值：0.8

###### cop_pool_size

- 描述：从 v5.0 引入，表示 TiFlash Coprocessor 最多同时执行的 cop 请求数量。如果请求数量超过了该配置指定的值，多出的请求会排队等待。如果设为 0 或不设置，则使用默认值，即物理核数的两倍。
- 默认值：0

###### batch_cop_pool_size

- 描述：从 v5.0 引入，表示 TiFlash Coprocessor 最多同时执行的 batch 请求数量。如果请求数量超过了该配置指定的值，多出的请求会排队等待。如果设为 0 或不设置，则使用默认值，即物理核数的两倍。
- 默认值：0

###### manual_compact_pool_size

- 描述：从 v6.1 引入，指定 TiFlash 执行来自 TiDB 的 ALTER TABLE ... COMPACT 请求时，能同时并行处理的请求数量。 如果这个值没有设置或设为了 0，则会采用默认值（1）。
- 默认值：1

###### dt_compression_method

- 描述：TiFlash 存储引擎的压缩算法，支持 LZ4、zstd 和 LZ4HC，大小写不敏感。默认使用 LZ4 算法。
- 默认值：LZ4

###### dt_compression_level

- 描述：TiFlash 存储引擎的压缩级别，默认为 1。 如果 dt_compression_method 设置为 LZ4，推荐将该值设为 1； 如果 dt_compression_method 设置为 zstd，推荐将该值设为 -1 或 1，设置为 -1 的压缩率更小，但是读性能会更好； 如果 dt_compression_method 设置为 LZ4HC，推荐将该值设为 9。
- 默认值：1

###### dt_page_gc_threshold

- 描述：从 v6.2.0 引入，表示 PageStorage 单个数据文件中有效数据的最低比例。当某个数据文件的有效数据比例低于该值时，会触发 GC 对该文件的数据进行整理。默认为 0.5。
- 默认值：0.5

###### max_bytes_before_external_group_by

- 描述：从 v7.0.0 引入，表示带 group by key 的 HashAggregation 算子在触发 spill 之前的最大可用内存，超过该阈值之后 HashAggregation 会采用 spill to disk 的方式来减小内存使用。默认值为 0，表示内存使用无限制，即不会触发 spill。
- 默认值：0

###### max_bytes_before_external_sort

- 描述：从 v7.0.0 引入，表示 sort/topN 算子在触发 spill 之前的最大可用内存，超过该阈值之后 sort/TopN 会采用 spill to disk 的方式来减小内存使用。默认值为 0，表示内存使用无限制，即不会触发 spill。
- 默认值：0

###### max_bytes_before_external_join

- 描述：从 v7.0.0 引入，表示带等值 join 条件的 HashJoin 算子在触发 spill 之前的最大可用内存，超过该阈值之后 HashJoin 算子会采用 spill to disk 的方式来减小内存使用。默认值为 0，表示内存使用无限制，即不会触发 spill。
- 默认值：0

###### enable_resource_control

- 描述：从 v7.4.0 引入，表示是否开启 TiFlash 资源管控功能。当设置为 true 时，TiFlash 会使用 Pipeline Model 执行模型。
- 默认值：True

#### security


### 配置文件 tiflash-learner.toml

`tiflash-learner.toml` 中的功能参数和 TiKV 基本一致，可以参照 [TiKV 配置](/tikv-configuration-file.md)来进行配置。下面只列了常用的部分参数。需要注意的是：

- 相对于 TiKV，TiFlash Proxy 新增了 `raftstore.snap-handle-pool-size` 参数。
- `key` 为 `engine` 的 `label` 是保留项，不可手动配置。

#### log

##### level

- TiFlash Proxy 的 log 级别，可选值为 "trace"、"debug"、"info"、"warn"、"error"，默认值为 "info"。从 v5.4.0 版本开始引入。
- 默认值：info

##### file

###### max-backups

- 可保留的 log 文件的最大数量。从 v5.4.0 版本开始引入。 如果未设置该参数或把该参数设置为默认值 `0`，TiFlash Proxy 会保存所有的日志文件； 如果把此参数设置为非 `0` 的值，TiFlash Proxy 最多会保留 `max-backups` 中指定数量的旧日志文件。比如，如果该值设置为 `7`，TiFlash Proxy 最多会保留 7 个旧的日志文件。
- 默认值：0

###### max-days

- 描述：保留 log 文件的最长天数。从 v5.4.0 版本开始引入。 如果未设置本参数或把此参数设置为默认值 `0`，TiFlash Proxy 会保存所有的日志文件。 如果把此参数设置为非 `0` 的值，在 `max-days` 之后，TiFlash Proxy 会清理过期的日志文件。
- 默认值：0

#### raftstore

##### apply-pool-size

- 描述：处理 Raft 数据落盘的线程池中线程的数量
- 默认值：4

##### store-pool-size

- 描述：处理 Raft 的线程池中线程的数量，即 Raftstore 线程池的大小。
- 默认值：4

##### snap-handle-pool-size

- 描述：控制处理 snapshot 的线程数，默认为 2。设为 0 则关闭多线程优化 TiFlash Proxy 特有参数，从 v4.0.0 版本开始引入。
- 默认值：2

#### security

##### encryption

###### data-encryption-method

- 描述：数据文件的加密方法。 可选值为 "aes128-ctr"、"aes192-ctr"、"aes256-ctr"、"sm4-ctr" (仅 v6.4.0 及之后版本) 和 "plaintext"。 默认值为 "plaintext"，即默认不开启加密功能。选择 "plaintext" 以外的值则表示启用加密功能。此时必须指定主密钥。
- 默认值：aes128-ctr

###### data-key-rotation-period

- 描述：轮换密钥的频率，默认值：`7d`。
- 默认值：168h

###### master-key

###### previous-master-key


### 通过拓扑 label 进行副本调度

[TiFlash 设置可用区](/tiflash/create-tiflash-replicas.md#设置可用区)

### 多盘部署

TiFlash 支持单节点多盘部署。如果你的部署节点上有多块硬盘，可以通过以下的方式配置参数，提高节点的硬盘 I/O 利用率。TiUP 中参数配置格式参照[详细 TiFlash 配置模版](/tiflash-deployment-topology.md#拓扑模版)。

#### TiDB 集群版本低于 v4.0.9

TiDB v4.0.9 之前的版本中，TiFlash 只支持将存储引擎中的主要数据分布在多盘上。通过 `path`（TiUP 中为 `data_dir`）和 `path_realtime_mode` 这两个参数配置多盘部署。

多个数据存储目录在 `path` 中以英文逗号分隔，比如 `/nvme_ssd_a/data/tiflash,/sata_ssd_b/data/tiflash,/sata_ssd_c/data/tiflash`。如果你的节点上有多块硬盘，推荐把性能最好的硬盘目录放在最前面，以更好地利用节点性能。

如果节点上有多块相同规格的硬盘，可以把 `path_realtime_mode` 参数留空（或者把该值明确地设为 `false`）。这表示数据会在所有的存储目录之间进行均衡。但由于最新的数据仍然只会被写入到第一个目录，因此该目录所在的硬盘会较其他硬盘繁忙。

如果节点上有多块规格不一致的硬盘，推荐把 `path_relatime_mode` 参数设置为 `true`，并且把性能最好的硬盘目录放在 `path` 参数内的最前面。这表示第一个目录只会存放最新数据，较旧的数据会在其他目录之间进行均衡。注意此情况下，第一个目录规划的容量大小需要占总容量的约 10%。

#### TiDB 集群版本为 v4.0.9 及以上

TiDB v4.0.9 及之后的版本中，TiFlash 支持将存储引擎的主要数据和新数据都分布在多盘上。多盘部署时，推荐使用 `[storage]` 中的参数，以更好地利用节点的 I/O 性能。但 TiFlash 仍然支持 [TiDB 集群版本低于 v4.0.9](#tidb-集群版本低于-v409) 中的参数。

如果节点上有多块相同规格的硬盘，推荐把硬盘目录填到 `storage.main.dir` 列表中，`storage.latest.dir` 列表留空。TiFlash 会在所有存储目录之间分摊 I/O 压力以及进行数据均衡。

如果节点上有多块规格不同的硬盘，推荐把 I/O 性能较好的硬盘目录配置在 `storage.latest.dir` 中，把 I/O 性能较一般的硬盘目录配置在 `storage.main.dir` 中。例如节点上有一块 NVMe-SSD 硬盘加上两块 SATA-SSD 硬盘，你可以把 `storage.latest.dir` 设为 `["/nvme_ssd_a/data/tiflash"]` 以及把 `storage.main.dir` 设为 `["/sata_ssd_b/data/tiflash", "/sata_ssd_c/data/tiflash"]`。TiFlash 会根据两个目录列表分别进行 I/O 压力分摊及数据均衡。需要注意此情况下，`storage.latest.dir` 中规划的容量大小需要占总规划容量的约 10%。

> **警告：**
>
> `[storage]` 参数从 TiUP v1.2.5 版本开始支持。如果你的 TiDB 版本为 v4.0.9 及以上，请确保你的 TiUP 版本不低于 v1.2.5，否则 `[storage]` 中定义的数据目录不会被 TiUP 纳入管理。
