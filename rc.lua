-- Standard awesome library
local gears = require("gears")
local awful = require("awful")
awful.rules = require("awful.rules")
require("awful.autofocus")
-- Widget and layout library
local wibox = require("wibox")
local vicious = require("vicious")
-- Theme handling library
local beautiful = require("beautiful")
-- Notification library
local naughty = require("naughty")
local menubar = require("menubar")

-- {{{ Error handling
-- Check if awesome encountered an error during startup and fell back to
-- another config (This code will only ever execute for the fallback config)
if awesome.startup_errors then
    naughty.notify({ preset = naughty.config.presets.critical,
                     title = "Oops, there were errors during startup!",
                     text = awesome.startup_errors })
end

-- Handle runtime errors after startup
do
    local in_error = false
    awesome.connect_signal("debug::error", function (err)
        -- Make sure we don't go into an endless error loop
        if in_error then return end
        in_error = true

        naughty.notify({ preset = naughty.config.presets.critical,
                         title = "Oops, an error happened!",
                         text = err })
        in_error = false
    end)
end
-- }}}

-- {{{ Variable definitions
-- Themes define colours, icons, and wallpapers
beautiful.init("/usr/share/awesome/themes/default/theme.lua")

-- This is used later as the default terminal and editor to run.
terminal = "xterm"
editor = os.getenv("EDITOR") or "nano"
editor_cmd = terminal .. " -e " .. editor

-- Default modkey.
-- Usually, Mod4 is the key with a logo between Control and Alt.
-- If you do not like this or do not have such a key,
-- I suggest you to remap Mod4 to another key using xmodmap or other tools.
-- However, you can use another modifier like Mod1, but it may interact with others.
modkey = "Mod4"

-- Table of layouts to cover with awful.layout.inc, order matters.
local layouts =
{
    awful.layout.suit.floating,
    awful.layout.suit.tile.left,
    awful.layout.suit.fair,
}
-- }}}

-- {{{ Wallpaper
if beautiful.wallpaper then
    for s = 1, screen.count() do
        gears.wallpaper.maximized(beautiful.wallpaper, s, true)
    end
end
-- }}}

-- {{{ Tags
-- Define a tag table which hold all screen tags.
tags = {}
for s = 1, screen.count() do
    -- Each screen has its own tag table.
    tags[s] = awful.tag({ 1, 2, 3, 4, 5, 6, 7, 8, 9 }, s, layouts[1])
end
-- }}}

-- {{{ Menu
-- Create a laucher widget and a main menu
myawesomemenu = {
   { "manual", terminal .. " -e man awesome" },
   { "edit config", editor_cmd .. " " .. awesome.conffile },
   { "restart", awesome.restart },
   { "quit", awesome.quit }
}

mymainmenu = awful.menu({ items = { { "Firefox", "firefox" },
                                    { "Explorer", "pcmanfm" },
                                    { "Notepad", "leafpad" },
                                    { "Terminal", terminal },
                                    { "Awesome", myawesomemenu },
                                    { "Shutdown", poweroff }
                                  }
                        })

mylauncher = awful.widget.launcher({ image = beautiful.awesome_icon,
                                     menu = mymainmenu })
mylauncher:buttons(awful.util.table.join(
                   awful.button({ }, 1, function ()
                                                  if instance then
                                                  instance:hide()
                                                  instance = nil
                                              else
                                                  instance = mymainmenu:toggle({ width=250 })
                                              end
                                        end),
                   awful.button({ }, 3, function ()
                                                  if instance then
                                                  instance:hide()
                                                  instance = nil
                                              else
                                                  instance = awful.menu.clients({ width=250 })
                                              end
                                        end)))

-- Menubar configuration
menubar.utils.terminal = terminal -- Set the terminal for applications that require it
-- }}}

-- {{{ Wibox

--Launcher
--launcher_explorer = awful.widget.launcher({ image = beautiful.awesome_icon,
--                                            command = "pcmanfm" })

--Separators
sep1 = wibox.widget.textbox()
sep1:set_text(" ")

sep2 = wibox.widget.textbox()
sep2:set_markup(' '..awful.tag.selected(1).name..'')
screen[1]:connect_signal("tag::history::update", function()
       sep2:set_markup(' '..awful.tag.selected(1).name..'')
end)

--icon_buffer = wibox.widget.textbox()
--icon_buffer:set_text("----")
--markup = wibox.widget.textbox()
--markup:set_text("")

--separator2:set_markup(' '..a..'')
--for clients on screen (HANDLED)
--markup append icon_buffer
--separator2:set_markup(' '..markup..'')

-- Create a textclock widget
mytextclock = awful.widget.textclock()
mytextclock:buttons(awful.util.table.join(awful.button({ }, 1,
function () naughty.notify({text = "it works"}) end)))



-- bat widget
batwidget = wibox.widget.textbox()
function batinfo(adapter)
	local fcur = io.open("/sys/class/power_supply/"..adapter.."/charge_now")    
	local fcap = io.open("/sys/class/power_supply/"..adapter.."/charge_full")
	local fsta = io.open("/sys/class/power_supply/"..adapter.."/status")
	local cur = fcur:read()
	local cap = fcap:read()
	local sta = fsta:read()
	local battery = math.floor(cur * 100 / cap)
	local batico = ""
	local batbar = ""
		
		if sta:match("Charged") then
			batbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶⮶⮶⮶ "  
			batico = "<span color='#dfdfdf'>⮎ </span>"
		else
			
			if tonumber(battery) > 95 then
				batbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶⮶⮶⮶</span><span color='#66666a'> </span>"
			elseif tonumber(battery) > 85 then
				batbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶ </span>"
			elseif tonumber(battery) > 75 then
				batbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶ </span>"
			elseif tonumber(battery) > 65 then
				batbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶ </span>"
			elseif tonumber(battery) > 55 then
				batbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶ </span>"
			elseif tonumber(battery) > 45 then
				batbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶ </span>"
			elseif tonumber(battery) > 35 then
				batbar = "<span color='#b4b4b4'>⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶⮶ </span>"
			elseif tonumber(battery) > 25 then
				batbar = "<span color='#b4b4b4'>⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶⮶⮶ </span>"
			elseif tonumber(battery) > 15 then
				batbar = "<span color='#d23d3d'>⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶⮶⮶⮶ </span>"
			elseif tonumber(battery) > 5 then
				batbar = "<span color='#d23d3d'>⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶⮶⮶⮶⮶ </span>"
			else
				batbar = "<span color='#d23d3d'></span><span color='#66666a'>⮶⮶⮶⮶⮶⮶⮶⮶⮶⮶ </span>"
			end 
			
			if sta:match("Charging") then
				batico = "<span color='#dfdfdf'>⮒ </span>"
			elseif sta:match("Discharging") then
				if tonumber(battery) > 49 then
					batico = "<span color='#dfdfdf'>⮏ </span>"
				elseif tonumber(battery) < 50 and tonumber(battery) > 25 then
					batico = "<span color='#dfdfdf'>⮑ </span>"
				else
					batico = "<span color='#c97c7c'>⮐ </span>"
				end 
			else
				batico = "<span color='#dfdfdf'>⮎ </span>"
			end
		end
		
	batwidget:set_markup(' '..batico..' '..batbar..'')
end 
battery_timer = timer({timeout = 1}) 
battery_timer:connect_signal("timeout", function()
	batinfo("BAT0")
end)
battery_timer:start()


--volume widget	
volwidget = wibox.widget.textbox()
vicious.register(volwidget, vicious.widgets.volume,
function (widget, args)
	if (args[2] ~= "♩" ) then
		if tonumber(args[1]) > 99 then
			volbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶⮶⮶⮶</span><span color='#66666a'> </span>"
		elseif tonumber(args[1]) > 90 then
			volbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶ </span>"
		elseif tonumber(args[1]) > 80 then
			volbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶ </span>"
		elseif tonumber(args[1]) > 70 then
			volbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶ </span>"
		elseif tonumber(args[1]) > 60 then
			volbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶ </span>"
		elseif tonumber(args[1]) > 50 then
			volbar = "<span color='#b4b4b4'>⮶⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶ </span>"
		elseif tonumber(args[1]) > 40 then
			volbar = "<span color='#b4b4b4'>⮶⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶⮶ </span>"
		elseif tonumber(args[1]) > 30 then
			volbar = "<span color='#b4b4b4'>⮶⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶⮶⮶ </span>"
		elseif tonumber(args[1]) > 20 then
			volbar = "<span color='#b4b4b4'>⮶⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶⮶⮶⮶ </span>"
		elseif tonumber(args[1]) > 10 then
			volbar = "<span color='#b4b4b4'>⮶</span><span color='#66666a'>⮶⮶⮶⮶⮶⮶⮶⮶⮶ </span>"
		else
			volbar = "<span color='#b4b4b4'></span><span color='#66666a'>⮶⮶⮶⮶⮶⮶⮶⮶⮶⮶ </span>"
		end 
		return '<span color="#dfdfdf"> ⮜ </span> '.. volbar ..' '
	else
		return '<span color="#dfdfdf"> ⮜ </span> [muted]'
	end 
end, 1, "Master")

-- Create a wibox for each screen and add it
mywibox = {}
mypromptbox = {}
mylayoutbox = {}
mytaglist = {}
mytaglist.buttons = awful.util.table.join(
                    awful.button({ }, 1, awful.tag.viewonly),
                    awful.button({ modkey }, 1, awful.client.movetotag),
                    awful.button({ }, 3, awful.tag.viewtoggle),
                    awful.button({ modkey }, 3, awful.client.toggletag),
                    awful.button({ }, 4, function(t) awful.tag.viewnext(awful.tag.getscreen(t)) end),
                    awful.button({ }, 5, function(t) awful.tag.viewprev(awful.tag.getscreen(t)) end)
                    )
mytasklist = {}
mytasklist.buttons = awful.util.table.join(
                     awful.button({ }, 1, function (c)
                                              if c == client.focus then
                                                  c.minimized = true
                                              else
                                                  -- Without this, the following
                                                  -- :isvisible() makes no sense
                                                  c.minimized = false
                                                  if not c:isvisible() then
                                                      awful.tag.viewonly(c:tags()[1])
                                                  end
                                                  -- This will also un-minimize
                                                  -- the client, if needed
                                                  client.focus = c
                                                  c:raise()
                                              end
                                          end),
                     awful.button({ }, 2, function (c)
                                              c:kill()
                                          end),
                     awful.button({ }, 3, function ()
                                              if instance then
                                                  instance:hide()
                                                  instance = nil
                                              else
                                                  instance = awful.menu.clients({ width=250 })
                                              end
                                          end),
                     awful.button({ }, 4, function ()
                                              awful.client.focus.byidx(1)
                                              if client.focus then client.focus:raise() end
                                          end),
                     awful.button({ }, 5, function ()
                                              awful.client.focus.byidx(-1)
                                              if client.focus then client.focus:raise() end
                                          end))

for s = 1, screen.count() do
    -- Create a promptbox for each screen
    mypromptbox[s] = awful.widget.prompt()
    -- Create an imagebox widget which will contains an icon indicating which layout we're using.
    -- We need one layoutbox per screen.
    mylayoutbox[s] = awful.widget.layoutbox(s)
    mylayoutbox[s]:buttons(awful.util.table.join(
                           awful.button({ }, 1, function () awful.layout.inc(layouts, 1) end),
                           awful.button({ }, 3, function () awful.layout.inc(layouts, -1) end),
                           awful.button({ }, 4, function () awful.layout.inc(layouts, 1) end),
                           awful.button({ }, 5, function () awful.layout.inc(layouts, -1) end)))
    -- Create a taglist widget
    mytaglist[s] = awful.widget.taglist(s, awful.widget.taglist.filter.all, mytaglist.buttons)

    -- Create a tasklist widget
    mytasklist[s] = awful.widget.tasklist(s, awful.widget.tasklist.filter.currenttags, mytasklist.buttons)

    -- Create the wibox
    mywibox[s] = awful.wibox({ position = "top", height = "28", screen = s })

    -- Widgets that are aligned to the left
    local left_layout = wibox.layout.fixed.horizontal()
    left_layout:add(mylauncher)
    left_layout:add(mypromptbox[s])
    left_layout:add(sep1)

    -- Widgets that are aligned to the right
    local right_layout = wibox.layout.fixed.horizontal()
    if s == 1 then right_layout:add(wibox.widget.systray()) end
    right_layout:add(mytaglist[s])
    right_layout:add(sep1)
    --right_layout:add(launcher_explorer)
    right_layout:add(batwidget)
    right_layout:add(volwidget)
    right_layout:add(mytextclock)
    right_layout:add(sep1)
    right_layout:add(sep2)
    --right_layout:add(mylayoutbox[s])

    -- Now bring it all together (with the tasklist in the middle)
    local layout = wibox.layout.align.horizontal()
    layout:set_left(left_layout)
    layout:set_middle(mytasklist[s])
    layout:set_right(right_layout)

    mywibox[s]:set_widget(layout)
end
-- }}}

-- {{{ Mouse bindings
root.buttons(awful.util.table.join(
    awful.button({ }, 3, function () mymainmenu:toggle() end),
    awful.button({ }, 4, awful.tag.viewnext),
    awful.button({ }, 5, awful.tag.viewprev)
))
-- }}}

-- {{{ Key bindings
globalkeys = awful.util.table.join(
    awful.key({ modkey,           }, "Left",   awful.tag.viewprev       ),
    awful.key({ modkey,           }, "Right",  awful.tag.viewnext       ),
    awful.key({ modkey,           }, "Escape", awful.tag.history.restore),

    awful.key({ modkey,           }, "j",
        function ()
            awful.client.focus.byidx( 1)
            if client.focus then client.focus:raise() end
        end),
    awful.key({ modkey,           }, "k",
        function ()
            awful.client.focus.byidx(-1)
            if client.focus then client.focus:raise() end
        end),
    awful.key({ modkey,           }, "w", function () mymainmenu:show() end),

    -- Layout manipulation
    awful.key({ modkey, "Shift"   }, "j", function () awful.client.swap.byidx(  1)    end),
    awful.key({ modkey, "Shift"   }, "k", function () awful.client.swap.byidx( -1)    end),
    awful.key({ modkey, "Control" }, "j", function () awful.screen.focus_relative( 1) end),
    awful.key({ modkey, "Control" }, "k", function () awful.screen.focus_relative(-1) end),
    awful.key({ modkey,           }, "u", awful.client.urgent.jumpto),
    awful.key({ modkey,           }, "Tab",
        function ()
            awful.client.focus.history.previous()
            if client.focus then
                client.focus:raise()
            end
        end),

    -- Standard program
    awful.key({ modkey,           }, "Return", function () awful.util.spawn(terminal) end),
    awful.key({ modkey, "Control" }, "r", awesome.restart),
    awful.key({ modkey, "Shift"   }, "q", awesome.quit),

    awful.key({ modkey,           }, "l",     function () awful.tag.incmwfact( 0.05)    end),
    awful.key({ modkey,           }, "h",     function () awful.tag.incmwfact(-0.05)    end),
    awful.key({ modkey, "Shift"   }, "h",     function () awful.tag.incnmaster( 1)      end),
    awful.key({ modkey, "Shift"   }, "l",     function () awful.tag.incnmaster(-1)      end),
    awful.key({ modkey, "Control" }, "h",     function () awful.tag.incncol( 1)         end),
    awful.key({ modkey, "Control" }, "l",     function () awful.tag.incncol(-1)         end),
    awful.key({ modkey,           }, "space", function () awful.layout.inc(layouts,  1) end),
    awful.key({ modkey, "Shift"   }, "space", function () awful.layout.inc(layouts, -1) end),

    awful.key({ modkey, "Control" }, "n", awful.client.restore),

    -- Prompt
    awful.key({ modkey },            "r",     function () mypromptbox[mouse.screen]:run() end),

    awful.key({ modkey }, "x",
              function ()
                  awful.prompt.run({ prompt = "Run Lua code: " },
                  mypromptbox[mouse.screen].widget,
                  awful.util.eval, nil,
                  awful.util.getdir("cache") .. "/history_eval")
              end),
    -- Menubar
    awful.key({ modkey }, "p", function() menubar.show() end),

    awful.key({ }, "XF86AudioMute", function () awful.util.spawn("amixer -c 0 set Master toggle") end),
    awful.key({ }, "XF86AudioRaiseVolume", function () awful.util.spawn("amixer -c 0 set Master 2+ unmute") end),
    awful.key({ }, "XF86AudioLowerVolume", function () awful.util.spawn("amixer -c 0 set Master 2-") end)
)

clientkeys = awful.util.table.join(
    awful.key({ modkey,           }, "f",      function (c) c.fullscreen = not c.fullscreen  end),
    awful.key({ modkey, "Shift"   }, "c",      function (c) c:kill()                         end),
    awful.key({ modkey, "Control" }, "space",  awful.client.floating.toggle                     ),
    awful.key({ modkey, "Control" }, "Return", function (c) c:swap(awful.client.getmaster()) end),
    awful.key({ modkey,           }, "o",      awful.client.movetoscreen                        ),
    awful.key({ modkey,           }, "t",      function (c) c.ontop = not c.ontop            end),
    awful.key({ modkey,           }, "n",
        function (c)
            -- The client currently has the input focus, so it cannot be
            -- minimized, since minimized clients can't have the focus.
            c.minimized = true
        end),
    awful.key({ modkey,           }, "m",
        function (c)
            c.maximized_horizontal = not c.maximized_horizontal
            c.maximized_vertical   = not c.maximized_vertical

            -- Remove border from windows that are maximized in both
            -- directions, and then re-add the default theme border when
            -- the window is restored.
            if c.maximized_vertical and c.maximized_horizontal then
              c.border_width = 0
            else
              c.border_width = beautiful.border_width
            end
        end)
)

-- Bind all key numbers to tags.
-- Be careful: we use keycodes to make it works on any keyboard layout.
-- This should map on the top row of your keyboard, usually 1 to 9.
for i = 1, 9 do
    globalkeys = awful.util.table.join(globalkeys,
        awful.key({ modkey }, "#" .. i + 9,
                  function ()
                        local screen = mouse.screen
                        local tag = awful.tag.gettags(screen)[i]
                        if tag then
                           awful.tag.viewonly(tag)
                        end
                  end),
        awful.key({ modkey, "Control" }, "#" .. i + 9,
                  function ()
                      local screen = mouse.screen
                      local tag = awful.tag.gettags(screen)[i]
                      if tag then
                         awful.tag.viewtoggle(tag)
                      end
                  end),
        awful.key({ modkey, "Shift" }, "#" .. i + 9,
                  function ()
                      local tag = awful.tag.gettags(client.focus.screen)[i]
                      if client.focus and tag then
                          awful.client.movetotag(tag)
                     end
                  end),
        awful.key({ modkey, "Control", "Shift" }, "#" .. i + 9,
                  function ()
                      local tag = awful.tag.gettags(client.focus.screen)[i]
                      if client.focus and tag then
                          awful.client.toggletag(tag)
                      end
                  end))
end

clientbuttons = awful.util.table.join(
    awful.button({ }, 1, function (c) client.focus = c; c:raise() end),
    awful.button({ modkey }, 1, awful.mouse.client.move),
    awful.button({ modkey }, 3, awful.mouse.client.resize))

-- Set keys
root.keys(globalkeys)
-- }}}

--ARCHIVED RULES
--border_width = beautiful.border_width

-- {{{ Rules
awful.rules.rules = {
    -- All clients will match this rule.
    { rule = { },
      properties = { border_width = beautiful.border_width,
                     border_color = beautiful.border_normal,
                     focus = awful.client.focus.filter,
                     keys = clientkeys,
                     buttons = clientbuttons, } },
    { rule = { class = "MPlayer" },
      properties = { floating = true } },
    { rule = { class = "pinentry" },
      properties = { floating = true } },
    { rule = { class = "gimp" },
      properties = { floating = true } },
    { rule = { class = "Dockx" },
      properties = { border_width = 0 } },

    -- Set Firefox to always map on tags number 2 of screen 1.
    -- { rule = { class = "Firefox" },
    --   properties = { tag = tags[1][2] } },
}
-- }}}

-- {{{ Signals
-- Signal function to execute when a new client appears.
client.connect_signal("manage", function (c, startup)
    -- Enable sloppy focus
    c:connect_signal("mouse::enter", function(c)
        if awful.layout.get(c.screen) ~= awful.layout.suit.magnifier
            and awful.client.focus.filter(c) then
            client.focus = c
        end
    end)

    if not startup then
        -- Set the windows at the slave,
        -- i.e. put it at the end of others instead of setting it master.
         awful.client.setslave(c)

        -- Put windows in a smart way, only if they does not set an initial position.
        if not c.size_hints.user_position and not c.size_hints.program_position then
            awful.placement.no_overlap(c)
            awful.placement.no_offscreen(c)
        end
    end

    local titlebars_enabled = false
    if titlebars_enabled and (c.type == "normal" or c.type == "dialog") then
        -- buttons for the titlebar
        local buttons = awful.util.table.join(
                awful.button({ }, 1, function()
                    client.focus = c
                    c:raise()
                    awful.mouse.client.move(c)
                end),
                awful.button({ }, 3, function()
                    client.focus = c
                    c:raise()
                    awful.mouse.client.resize(c)
                end)
                )

        -- Widgets that are aligned to the left
        local left_layout = wibox.layout.fixed.horizontal()
        --left_layout:add(awful.titlebar.widget.iconwidget(c))
        left_layout:buttons(buttons)

        -- Widgets that are aligned to the right
        local right_layout = wibox.layout.fixed.horizontal()
        --right_layout:add(awful.titlebar.widget.floatingbutton(c))
        --right_layout:add(awful.titlebar.widget.stickybutton(c))
        --right_layout:add(awful.titlebar.widget.ontopbutton(c))
        --right_layout:add(awful.titlebar.widget.maximizedbutton(c))
        --right_layout:add(awful.titlebar.widget.closebutton(c))

        -- The title goes in the middle
        local middle_layout = wibox.layout.flex.horizontal()
        local title = awful.titlebar.widget.titlewidget(c)
        title:set_align("center")
        --middle_layout:add(title)
        middle_layout:buttons(buttons)

        -- Now bring it all together
        local layout = wibox.layout.align.horizontal()
        layout:set_left(left_layout)
        layout:set_right(right_layout)
        layout:set_middle(middle_layout)

        awful.titlebar(c):set_widget(layout)
    end
end)

client.connect_signal("focus", function(c) c.border_color = beautiful.border_focus end)
client.connect_signal("unfocus", function(c) c.border_color = beautiful.border_normal end)
-- }}}

--Startup
--do
--  local cmds = 
--  { 
--    "dockx",
--  }

--  for _,i in pairs(cmds) do
--    awful.util.spawn(i)
--  end
--end
