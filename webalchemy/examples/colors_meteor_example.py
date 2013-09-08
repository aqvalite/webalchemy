#
# trying to reconstruct Meteor color application
#
import logging

from tornado import gen
from webalchemy import server
from webalchemy.widgets.basic.menu import menu

log= logging.getLogger(__name__)
log.setLevel(logging.INFO)

class colors_meteor_app:    

    # shared state between sessions in process
    colors_count={
        'foo'             :0,
        'bar'             :0,
        'wowowowowo!!!'   :0,
        'this is cool'    :0,
        'WEBALCHEMY ROCKS':0,
    }

    @staticmethod
    def prepare_for_general_reload():
        return colors_meteor_app.colors_count

    @staticmethod
    def recover_from_general_reload(colors_count):
        for color in colors_meteor_app.colors_count.keys():
            if color in colors_count:
                colors_meteor_app.colors_count[color]= colors_count[color]

    # this method is called when a new session starts
    @gen.coroutine
    def initialize(self, remotedocument, wshandler, message):
        # remember these for later use
        self.rdoc= remotedocument
        self.wsh= wshandler
        log.info('New session openned, id='+self.wsh.id)
        # insert a menu into the page
        self.menu= self.build_menu()
        self.rdoc.body.append(self.menu.element)

    # register the method so we can call it from frontend js,
    # and then also from other sessions (from Python)
    @server.jsrpc
    @server.pyrpc
    @gen.coroutine
    def button_clicked(self, sender_id, item_id, color):
        if sender_id==self.wsh.id:
            # button clicked on this session
            colors_meteor_app.colors_count[color]+= 1
            self.wsh.rpc(self.button_clicked, item_id, color)
        else:
            # button clicked by other session
            log.info('got an update...')
            item= self.menu.id_dict[item_id]
            self.menu.increase_count_by(item, 1)

    def build_menu(self):
        # the following function will be used to initialize all menu items
        def on_add(item):
            nonlocal m
            color= item.text
            item.app.color= color
            item.app.clickedcount= colors_meteor_app.colors_count[color]
            m.increase_count_by(item,0)
        # create a menu element with the above item initializer
        m= menu(self.rdoc, on_add)
        # function to increase the count in front-end
        m.increase_count_by= self.rdoc.jsfunction('element','amount',body='''
            att= element.app;
            att.clickedcount+= amount;
            if (att.clickedcount>0.5) {
                element.textContent= '('+att.clickedcount+') '+att.color;
            }''')
        m.element.events.add(click= self.rdoc.jsfunction('event',body='''
            att= event.target.app;
            rpc('button_clicked', event.target.id, att.color);
            #{m.increase_count_by}(event.target,1);
        '''))
        # style the menu
        m.rule_menu.style(display='table',margin='10px')
        m.rule_item.style(
            color='#000000',
            fontSize='2em',
            textTransform='uppercase',
            fontFamily='Arial, Verdana, Sans-serif',
            float='bottom',
            padding='10px',
            listStyle='none',
            cursor='pointer',
            webkitTransition='all 0.3s linear',
            webkitUserSelect='none'
        )
        m.rule_item_hover.style(
            color='#ffffff',
            background='#000000',
            paddingLeft='20px',
            webkitTransform='rotate(5deg)'
        )
        # populate the menu with shared colors dict
        for color in colors_meteor_app.colors_count:
            m.add_item(color)
        return m

