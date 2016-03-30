class Dashing.Dev extends Dashing.Widget

  ready: ->
    @services = []
    @checks = []
    @locations = []
    @t = {}
    @prev_t = {}

    tbl = document.createElement('div')
    tblId = "table_" + @id
    tbl.setAttribute('id', tblId)
    document.getElementById(@id).appendChild(tbl)

  refresh: ->
    for i in @locations
      if not @t[i]?
        l = {}
      else
        l = @t[i]
      for j in @services
        if not l[j]?
          s = {}
        else
          s = l[j]
        for k in @checks
          if not s[k]?
            s[k] = ""
        l[j] = s
      @t[i] = l

  onData: (data) ->
    if not @t
      @ready()

    for i in data.items
      if i.location not in @locations
        @locations.push(i.location)
        @locations.sort()
        @refresh()

      if i.service not in @services
        @services.push(i.service)
        @services.sort()
        @refresh()

      if i.check not in @checks
        @checks.push(i.check)
        @checks.sort()
        @refresh()

      @t[i.location][i.service][i.check] = i.value

    tbl = "<table><tr><th></th>"
    for i in @locations
      tbl += "<th>" + i + "</th>"

    tbl += "</tr>"
    rowscount = @checks.length + 1

    for i in @services
      tbl += "<tr><td rowspan=" + rowscount + " style='border-bottom:2px solid black;'>" + i + "</td>"
      opentag = 0
      for j in @checks
        if opentag = 1
          tbl += "<tr>"
        for k in @locations
          switch @t[k][i][j]
            when 'OK' then tbl += "<td style='background-color: #30C830'>" + j + "</td>"
            when 'FAIL' then tbl += "<td style='background-color: #FF0000'>" + j + "</td>"
            when 'NONE' then tbl += "<td style='background-color: #C0C0C0'>" + j + "</td>"
            when 'RUN' then (
              if @prev_t[k]? and @prev_t[k][i]? and @prev_t[k][i][j]?
                switch @prev_t[k][i][j]
                  when 'OK' then tbl += "<td style='background: linear-gradient(to left, #F0A060 0%,#30C830 100%)'>" + j + "</td>"
                  when 'FAIL' then tbl += "<td style='background: linear-gradient(to left, #F0A060 0%,#FF0000 100%)'>" + j + "</td>"
                  when 'WARN' then tbl += "<td style='background: linear-gradient(to left, #F0A060 0%,#F0E241 100%)'>" + j + "</td>"
                  else tbl += "<td style='background-color: #F0A060'>" + j + "</td>"
              else
                tbl += "<td style='background-color: #F0A060'>" + j + "</td>"
            )
            when 'WARN' then tbl += "<td style='background-color: #F0E241'>" + j + "</td>"
            else tbl += "<td>" + j + "</td>"
        tbl += "</tr>"
        opentag = 1
      tbl += "</tr>"

    tbl += "</table>"
    document.getElementById("table_" + data.id).innerHTML = tbl

    for i in @locations
      if not @prev_t[i]?
        @prev_t[i] = {}
      for j in @services
        if not @prev_t[i][j]?
          @prev_t[i][j] = {}
        for k in @checks
          if @t[i][j][k] != 'RUN'
            @prev_t[i][j][k] = @t[i][j][k]
          if not @prev_t[i][j][k]?
            @prev_t[i][j][k] = @t[i][j][k]
