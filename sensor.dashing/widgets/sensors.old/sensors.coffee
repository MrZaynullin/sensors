class Dashing.Sensors extends Dashing.Widget

  ready: ->
    @services = ['ZV', 'ZVNAT', 'HN', 'BLOCK', 'CORP', 'WIFI']
    @checks = ['dhcp', 'ping', 'dns', 'http', 'torrent']
    @t = {}

    for i in @services
      res = {}
      for j in @checks
        res[j] = ""
      @t[i] = res

    table = document.createElement('div')
    tableId = "table_" + @id
    table.setAttribute('id', tableId)
    document.getElementById(@id).appendChild(table)

  onData: (data) ->
    if not @t
      @ready()

    items = data.items

    for i in items
      @t[i.service][i.check] = i.value

#    debugger

    document.getElementById("table_" + data.id).innerHTML = tbl

    tbl = "<table><tr><th></th>"
    for i in @services
      tbl += "<th>" + i + "</th>"

    tbl += "</tr>"

    for i in @checks
      tbl += "<tr><td align='left'>" + i + "</td>"
      for j in @services
        switch @t[j][i]
          when 'OK' then tbl += "<td>" + @t[j][i] + "</td>"
          when 'FAIL' then tbl += "<td style='background-color: #FF0000'>" + @t[j][i] + "</td>"
          when 'NONE' then tbl += "<td style='background-color: #E9E27B'>" + @t[j][i] + "</td>"
          when 'RUN' then tbl += "<td style='background-color: #F7AE48'>" + @t[j][i] + "</td>"
          when 'WARN' then tbl += "<td style='background-color: #F5EC33'>" + @t[j][i] + "</td>"
          else tbl += "<td>" + @t[j][i] + "</td>"
      tbl += "</tr>"

    tbl += "</table>"

    document.getElementById("table_" + data.id).innerHTML = tbl
