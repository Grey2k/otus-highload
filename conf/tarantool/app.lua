function count_profiles()
    return box.space.soc_net_profiles:count()
end


function search_profiles(first_name, last_name, page, cnt)

    local cnt_sql = string.format(
        'SELECT count(*) FROM "soc_net_profiles" WHERE "first_name" LIKE \'%s\' AND "last_name" LIKE \'%s\'',
         first_name, last_name
    )

    local sql = string.format(
        'SELECT * FROM "soc_net_profiles" WHERE "first_name" LIKE \'%s\' AND "last_name" LIKE \'%s\' LIMIT %d, %d',
         first_name, last_name, (page - 1) * cnt, cnt
    )

    return {cnt=box.execute(cnt_sql).rows[1][1], items=box.execute(sql).rows}
end

function cleanup_feed_cache(feed_id, max_items)
    local total_items = box.space.feed.index.feed_id:count(feed_id)
    if max_items >= total_items then
        return
    end
    local limit = total_items - max_items
    for _, item in pairs(box.space.feed.index.feed_id:select(feed_id, { iterator = 'EQ', limit = limit })) do
        box.space.feed:delete(item[1])
    end
end
