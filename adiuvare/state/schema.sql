create table if not exists audit_events (
    id integer primary key autoincrement,
    identity text not null,
    endpoint text not null,
    score real not null,
    verdict text not null,
    breakdown_json text not null,
    created_at text default current_timestamp
);

create table if not exists identity_state (
    identity text primary key,
    seen integer not null,
    score_ewma real not null,
    blocked_until real not null
);

create table if not exists config_history (
    id integer primary key autoincrement,
    patch_json text not null,
    created_at text default current_timestamp
);
