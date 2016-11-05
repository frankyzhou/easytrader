__author__ = 'frankyzhou'
import os
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import subprocess

# path to the firefox binary inside the Tor package
binary = 'F:\\Soft\\Tor Browser\\Browser\\firefox.exe'
profile = 'F:\\Soft\\Tor Browser\\Browser\\TorBrowser\\Data\\Browser\\profile.default'
firefox_binary = FirefoxBinary(binary)
ff_prof = FirefoxProfile(profile)

#set some privacy settings

ff_prof.set_preference( "places.history.enabled", False )
ff_prof.set_preference( "privacy.clearOnShutdown.offlineApps", True )
ff_prof.set_preference( "privacy.clearOnShutdown.passwords", True )
ff_prof.set_preference( "privacy.clearOnShutdown.siteSettings", True )
ff_prof.set_preference( "privacy.sanitize.sanitizeOnShutdown", True )
ff_prof.set_preference( "signon.rememberSignons", False )
ff_prof.set_preference( "network.cookie.lifetimePolicy", 2 )
ff_prof.set_preference( "network.dns.disablePrefetch", True )
ff_prof.set_preference( "network.http.sendRefererHeader", 0 )

#set socks proxy
ff_prof.set_preference( "network.proxy.type", 1 )
ff_prof.set_preference( "network.proxy.socks_version", 5 )
ff_prof.set_preference( "network.proxy.socks", '127.0.0.1' )
ff_prof.set_preference( "network.proxy.socks_port", 9050 )
ff_prof.set_preference( "network.proxy.socks_remote_dns", True )

#if you're really hardcore about your security
#js can be used to reveal your true i.p.
ff_prof.set_preference( "javascript.enabled", False )

#get a huge speed increase by not downloading images
ff_prof.set_preference( "permissions.default.image", 2 )

##
# programmatically start tor (in windows environment)
# ##
tor_path = "F:\\Soft\\Tor Browser\\Browser\\TorBrowser\\Tor\\"
torrc_path = "F:\\Soft\\Tor Browser\\Browser\\TorBrowser\\Data\\Tor\\torrc"
#
DETACHED_PROCESS = 0x00000008
# #calling as a detached_process means the program will not die with your python program - you will need to manually kill it
# ##
# # somebody please let me know if there's a way to make this a child process that automatically dies (in windows)
# ##
tor_process = subprocess.Popen( '"' + tor_path+'tor.exe" --nt-service "-f" "' + torrc_path + '"')
#
# #attach to tor controller
# ## imports ##
from stem import *
from stem.control import Controller
import stem
##
with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)
#
# #in your torrc, you need to store the hashed version of 'password' which you can get with: subprocess.call( '"' + tor_path+'tor.exe" --hash-password %s' %control_password )
#
#
# #check that everything is good with your tor_process by checking bootstrap status
# tor_controller.send( 'GETINFO status/bootstrap-phase' )
# response = tor_controller.recv()
# response = response.content()

#I will leave handling of response status to you

browser = None
def get_browser(binary=None):
    global browser
    # only one instance of a browser opens, remove global for multiple instances
    if not browser:
        browser = webdriver.Firefox(firefox_binary=binary)
    return browser

if __name__ == "__main__":
    browser = get_browser(binary=firefox_binary)

    urls = (
        ('tor browser check', 'https://check.torproject.org/'),
        ('ip checker', 'http://icanhazip.com')
    )
    for url_name, url in urls:
        print "getting", url_name, "at", url
        browser.get(url)
        print browser.page_source