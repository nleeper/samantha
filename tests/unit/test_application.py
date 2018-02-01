from mock import patch
from pytest_mock import mocker

from handlers.facebook import FacebookHandler
from handlers.pipeline import PipelineHandler

from application import WebApplication

@patch('application.tornado.web.Application.__init__')
@patch('application.ChatProcessor')
@patch('application.PluginManager')
@patch('application.PipelineManager')
def test_application_setup(pipeline_mgr, plugin_mgr, chat_processor, tornado_web_app):
    app = WebApplication()

    assert app.pipeline is pipeline_mgr

    pipeline_mgr.assert_called_once()
    plugin_mgr.assert_called_once_with(app._pipeline_manager)
    chat_processor.assert_called_once_with(app._plugin_manager)

    tornado_web_app.assert_called_once_with(app, [(r'/ws/pipeline', PipelineHandler), (r'/facebook', FacebookHandler)])

def test_initialize():
    pass