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

function cutoff_feed(feed_id, max_items)
    local total_items = 0
    for _, item in pairs(box.space.feed.index.feed_id:select(feed_id, { iterator = 'REQ', limit = limit })) do
        total_items = total_items + 1
        if total_items > max_items then
            box.space.feed:delete({item[1], item[2]})
        end
    end
end

function clear_feed(feed_id)
    for _, item in box.space.feed.index.feed_id:pairs({feed_id}) do
        box.space.feed:delete({item[1], item[2]})
    end
end