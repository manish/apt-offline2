# -*- coding: utf-8 -*-

import threading

WindowColor = True
try:
        import WConio
except ImportError:
        WindowColor = False

class Log:
        '''A OOP implementation for logging.
            warnings is to tackle the warning option
            verbose is to tackle the verbose option
            color is if you want to colorize your output
    
            You should pass these options, taking it from optparse/getopt,
            during instantiation'''
            
        #            WConio can provide simple coloring mechanism for Microsoft Windows console
        #            Color Codes:
        #            Black = 0
        #            Green = 2
        #            Red = 4
        #            White = 15
        #            Light Red = 12
        #            Light Cyan = 11
        #            
        #            #FIXME: The Windows Command Interpreter does support colors natively. I think that support has been since Win2k.
        #            That's all for Windows Command Interpreter.
        #            
        #            As for ANSI Compliant Terminals (which most Linux/Unix Terminals are.).....
        #            I think the ANSI Color Codes would be good enough for my requirements to print colored text on an ANSI compliant terminal.
        #
        #            The ANSI Terminal Specification gives programs the ability to change the text color or background color.
        #            An ansi code begins with the ESC character [^ (ascii 27) followed by a number (or 2 or more separated by a semicolon) and a letter.
        #    
        #            In the case of colour codes, the trailing letter is "m"...
        #    
        #            So as an example, we have ESC[31m ... this will change the foreground colour to red.
        #    
        #            The codes are as follows:
        #    
        #            For Foreground Colors
        #            1m - Hicolour (bold) mode
        #            4m - Underline (doesn't seem to work)
        #            5m - BLINK!!
        #            8m - Hidden (same colour as bg)
        #            30m - Black
        #            31m - Red
        #            32m - Green
        #            33m - Yellow
        #            34m - Blue
        #            35m - Magenta
        #            36m - Cyan
        #            37m - White
        #    
        #            For Background Colors
        #    
        #            40m - Change Background to Black
        #            41m - Red
        #            42m - Green
        #            43m - Yellow
        #            44m - Blue
        #            45m - Magenta
        #            46m - Cyan
        #            47m - White
        #    
        #            7m - Change to Black text on a White bg
        #            0m - Turn off all attributes.
        #    
        #            Now for example, say I wanted blinking, yellow text on a magenta background... I'd type ESC[45;33;5m
        
        def __init__( self, verbose, lock=None ):
                self.VERBOSE = bool( verbose )
                self.color_syntax = '\033[1;'
                
                if lock is True:
                        self.DispLock = threading.Lock()
                        self.lock = True
                else:
                        self.DispLock = False
                        self.lock = False
                
                if os.name == 'posix':
                        self.platform = 'posix'
                        self.color = {'Red': '31m', 'Black': '30m',
                                      'Green': '32m', 'Yellow': '33m',
                                      'Blue': '34m', 'Magneta': '35m',
                                      'Cyan': '36m', 'White': '37m',
                                      'Bold_Text': '1m', 'Underline': '4m',
                                      'Blink': '5m', 'SwitchOffAttributes': '0m'}
           
                elif os.name in ['nt', 'dos']:
                        self.platform = None
            
                        if WindowColor is True:
                                self.platform = 'microsoft'
                                self.color = {'Red': 4, 'Black': 0,
                                              'Green': 2, 'White': 15,
                                              'Cyan': 11, 'SwitchOffAttributes': 15}
                else:
                        self.platform = None
                        self.color = None
        
        def set_color( self, color ):
                '''Check the platform and set the color'''
                if self.platform == 'posix':
                        sys.stdout.write( self.color_syntax + self.color[color] )
                        sys.stderr.write( self.color_syntax + self.color[color] )
                elif self.platform == 'microsoft':
                        WConio.textcolor( self.color[color] )
        
        def msg( self, msg ):
                '''Print general messages. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire( True )
          
                #self.set_color( 'White' )
                sys.stdout.write( msg )
                sys.stdout.flush()
                #self.set_color( 'SwitchOffAttributes' )
        
                if self.lock:
                        self.DispLock.release()
        
        def err( self, msg ):
                '''Print messages with an error. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire( True )
            
                self.set_color( 'Red' )
                sys.stderr.write( "ERROR: " + msg )
                sys.stderr.flush()
                self.set_color( 'SwitchOffAttributes' )
        
                if self.lock:
                        self.DispLock.release()
        
        def success( self, msg ):
                '''Print messages with a success. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire( True )
            
                self.set_color( 'Green' )
                sys.stdout.write( msg )
                sys.stdout.flush()
                self.set_color( 'SwitchOffAttributes' )
        
                if self.lock:
                        self.DispLock.release()

        
        # For the rest, we need to check the options also
        def verbose( self, msg ):
                '''Print verbose messages. If locking is available use them.'''
                if self.lock:
                        self.DispLock.acquire( True )
                
                if self.VERBOSE is True:
                        self.set_color( 'Cyan' )
                        sys.stdout.write( "VERBOSE: " + msg )
                        sys.stdout.flush()
                        self.set_color( 'SwitchOffAttributes' )
        
                if self.lock:
                        self.DispLock.release()