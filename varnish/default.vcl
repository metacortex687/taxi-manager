vcl 4.1;

backend default {
    .host = "nginx";
    .port = "80";

    .connect_timeout = 1s;
    .first_byte_timeout = 60s;
    .between_bytes_timeout = 60s;
}

sub vcl_recv {
    # Кэшируем только безопасные read-запросы.
    # POST/PUT/PATCH/DELETE не трогаем.
    if (req.method != "GET" && req.method != "HEAD") {
        return (pass);
    }

    # Кэшируем только чтение моделей/брендов.
    # Остальные API не трогаем, чтобы не смешать пользовательские данные.
    if (
        req.url ~ "^/api/v1/rust/models/[0-9]+/$" ||
        req.url ~ "^/api/v1/rust/models/batch-queue/[0-9]+/$" ||
        req.url ~ "^/api/v1/models/[0-9]+/$"
    ) {
        # Authorization НЕ удаляем.
        # Он будет передан Nginx/Django, но не войдёт в стандартный cache key.

        # Cookie тоже обычно ломает кэширование и может делать ответ персональным.
        unset req.http.Cookie;

        return (hash);
    }

    return (pass);
}

sub vcl_backend_response {
    if (
        bereq.url ~ "^/api/v1/rust/models/[0-9]+/$" ||
        bereq.url ~ "^/api/v1/rust/models/batch-queue/[0-9]+/$" ||
        bereq.url ~ "^/api/v1/models/[0-9]+/$"
    ) {
        # Для теста держим объект в кэше 60 секунд.
        set beresp.ttl = 60s;
        set beresp.grace = 30s;

        unset beresp.http.Set-Cookie;

        return (deliver);
    }
}

sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }

    set resp.http.X-Cache-Hits = obj.hits;
}