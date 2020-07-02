request = function()
  page = math.random(1, 500)
  path = "/?page=" .. page
  return wrk.format("GET", path)
end
