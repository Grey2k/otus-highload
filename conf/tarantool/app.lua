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