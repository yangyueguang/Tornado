create table extract_record (
    doc_id     number(20) primary key, --研报ID
    hisotry_id number(20) not null, -- 抽取记录内部 ID
    doc_type   number(3) not null, -- 文档类型
    pdf_path   varchar2(100) not null, -- 研报保存路径
    status     varchar2(50) default 'OK', -- 接口返回状态
    error_code number(5) default 0, -- 错误返回码
    error_msg  varchar2(100) default '', -- 错误返回消息内容
    create_time	date default sysdate not null, -- 首次解析时间
    update_time	date default sysdate not null -- 更新解析时间
);
create table extract_item (
    doc_id	   number (20) not null, -- 研报ID
    item_id	   number (5) not null, -- 文本字段id
    item_name  varchar2(100) default '', -- 文本字段名称
    word	   varchar2(1000) default '', -- 抽取的值
    confidence number (5,3) default 0 -- 置信度
);
create table extract_table (
    doc_id	   number (20) not null, -- 研报ID
    table_id   number (5) not null, -- 表格ID
    table_name varchar2(50) default '', -- 表格名称
    table_path varchar2(200) default '' -- 表格保存的路径
);