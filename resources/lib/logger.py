import xbmc


class Logger(object):
    def __init__(self, name=None):
        self.name = name

    def _log(self, msg, level):
        if self.name:
            msg = "{0}: {1}".format(self.name, msg)
        xbmc.log(msg, level)

    def debug(self, msg):
        """
        In depth information about the status of Kodi. This information can pretty much only be deciphered by a developer or long time Kodi power user.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGDEBUG)

    def info(self, msg):
        """
        Something has happened. It's not a problem, we just thought you might want to know. Fairly excessive output that most people won't care about.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGINFO)

    def notice(self, msg):
        """
        Similar to INFO but the average Joe might want to know about these events. This level and above are logged by default.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGNOTICE)

    def warning(self, msg):
        """
        Something potentially bad has happened. If Kodi did something you didn't expect, this is probably why. Watch for errors to follow.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGWARNING)

    def error(self, msg):
        """
        This event is bad. Something has failed. You likely noticed problems with the application be it skin artifacts, failure of playback a crash, etc.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGERROR)

    def fatal(self, msg):
        """
        We're screwed. Kodi is about to crash.

        :param msg: The log message.
        :return:
        """
        self._log(msg, xbmc.LOGFATAL)
