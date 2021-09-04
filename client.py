import socket
import sys
import os
import logging
import time
from PIL import Image, ImageDraw, ImageFont
import datetime
import pytz
from weather import WeatherClient

if socket.gethostname() == os.getenv("PRODUCTION_HOSTNAME"):
    DEBUG = False
else:
    DEBUG = True
if not DEBUG:
    from lib.waveshare_epd import epd7in5_V2


class EpaperClient(object):
    debug = DEBUG
    screen_width = 800
    screen_height = 480
    logging.basicConfig(level=logging.DEBUG)
    # if DEBUG:
    project_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "epaper"
    )
    picdir = os.path.join(project_dir, "pic")
    libdir = os.path.join(project_dir, "lib")
    fonts_dir = os.path.join(project_dir, "fonts")
    local_file_dir = os.path.join(project_dir, "media")
    small_font = ImageFont.truetype(os.path.join(fonts_dir, "OpenSans-Regular.ttf"), 16)
    font_awesome = ImageFont.truetype(
        os.path.join(fonts_dir, "fonts/fa-regular-400.ttf"), 30
    )
    font_awesome_solid = ImageFont.truetype(
        os.path.join(fonts_dir, "fonts/fa-solid-900.ttf"), 30
    )
    # font awesome icons
    # Most use FA Solid instead of regular. See FA docs
    sun = chr(0xF185)
    cloudy = chr(0xF0C2)
    rain = chr(0xF73D)
    heavy_rain = chr(0xF73D)
    wind = chr(0xF72E)

    def __init__(self):
        if os.path.exists(self.libdir):
            sys.path.append(self.libdir)
        # if os.path.exists(self.fonts_dir):
        #     sys.path.append(self.fonts_dir)
        if self.debug and not os.path.exists(self.local_file_dir):
            os.mkdir(self.local_file_dir)
        self.setup()

    def setup(self):
        if not DEBUG:
            self.epd = epd7in5_V2.EPD()
            logging.info("init and Clear")
            self.epd.init()
            self.epd.Clear()
            self.screen_width = self.epd.width
            self.screen_height = self.epd.height

    def get_time(self):
        tz = pytz.timezone(os.getenv("TIMEZONE"))
        now = datetime.datetime.now().astimezone(tz)
        now_str = now.strftime("%A %B %d, %Y")
        return now_str

    def draw(self):
        # Drawing on the Horizontal image
        logging.info("1. Drawing on the Horizontal image. Testing...")
        image = Image.new(
            "1", (self.screen_width, self.screen_height), 255
        )  # 255: clear the frame
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            (0, 0, self.screen_width, self.screen_height), outline=0, fill=255
        )

        # display weather from weather API
        self.draw_weather(draw)

        # todo: Add chart
        # self.draw_chart(draw)
        return image

    def draw_weather(self, draw):
        """Parse weather JSON and output weather forecast for the next 7 days"""
        forecast = self.get_weather()
        start_x = 300
        start_y = 25
        for day in forecast:
            temp = day["temp"] + chr(176)
            start_x_text = start_x + 5
            draw.text((start_x_text, start_y), temp, 0, self.small_font)
            weather_icon = self.get_weather_icon(day["type"])
            draw.text(
                (start_x, start_y + 30),
                weather_icon,
                0,
                self.font_awesome_solid,
            )
            draw.text((start_x_text, start_y + 75), day["day"], 0, self.small_font)
            start_x += 60

    def get_weather_icon(self, weather_type):
        """Return Font Awesome icon for the Weather type e.g. rain / sun / etc"""
        print(weather_type)
        if not weather_type:
            return self.sun
        return {
            "Rain": self.rain,
            "Sunny": self.sun,
            "Clouds": self.cloudy,
            "Clear": self.sun,
        }.get(weather_type, self.sun)

    def display(self):
        """Full-refresh every 60 mins since e-ink display shouldn't be refreshed quickly."""
        while True:
            image = self.draw()
            if DEBUG:
                # display in an image file
                local_file = "{}/output.png".format(self.local_file_dir)
                logging.info(local_file)
                image.save(local_file, "PNG")
                image.show()
                exit()
            else:
                # display on e-ink
                self.epd.display(self.epd.getbuffer(image))
                time.sleep(3600)

    def clear(self):
        self.epd.init()
        self.epd.Clear()
        logging.info("Goto Sleep...")
        self.epd.sleep()
        epd7in5_V2.epdconfig.module_exit()

    def get_weather(self):
        """
        Return weather JSON for use in display
        """
        weather = WeatherClient()
        forecast = weather.get_weather_forecast_list()
        return forecast

    def draw_chart(self, draw):
        """
        Create a line chart given a bunch of x and y points
        """
        # todo: get a bunch of prices over a period of time for BTC, say last 7 days and draw a line graph
        # x axis is time (in days)
        # y axis is price
        x = [0, 50, 100, 150, 200, 250, 300]
        # todo: plug in last 7 hours of BTC prices here
        prices = [61000, 59000, 63000, 64000, 65000, 66000, 67000]
        # convert prices to a number in the range 0 - 300
        y = []
        for price in prices:
            y.append(self.get_compressed_value(price, prices))
        print(x)
        print(y)
        # x = [167, 109, 80, 69, 58, 31]
        # y = [140, 194, 227, 232, 229, 229]
        # draw a line between each x and y point to display the chart
        draw.line(list(zip(x, y)), fill=0, width=2)

    def get_compressed_value(self, price, prices):
        """
        Calculate the 'compressed' version of number, that is the number between a new set of ranges.
        E.g. I want 67,000 to be in a new range between 0 and 300
        """
        old_max = max(prices)
        old_min = min(prices)
        old_range = old_max - old_min
        new_max = 200
        new_min = 100
        new_range = new_max - new_min
        new_value = (((price - old_min) * new_range) / old_range) + new_min
        # the new value now needs to be reversed to go in the right direction on the display
        new_value = (new_max - new_value) + new_min
        return new_value


client = EpaperClient()
try:
    client.display()
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    logging.info("Clear...")
    if not DEBUG:
        client.clear()
    exit()
