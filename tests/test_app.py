from unittest.mock import MagicMock, patch
from reviewcheck.app import show_reviews

def test_show_reviews_no_mrs(capsys):
    config = {
        "secret_token": "token",
        "api_url": "http://gitlab.com",
        "project_ids": ["1"],
        "user": "USER",
        "ignored_mrs": [],
        "show_all_discussions": False,
        "hide_replied_discussions": False,
        "output_width": 80,
        "jira_url": "http://jira.com",
    }
    
    with patch("reviewcheck.app.requests.Session") as mock_session, \
         patch("reviewcheck.app.read_viewed_message_ids", return_value=set()), \
         patch("reviewcheck.app.write_viewed_message_ids"), \
         patch("reviewcheck.app.console") as mock_console:
        
        # Mock response for MRs: empty list
        mock_response = MagicMock()
        mock_response.content = b"[]"
        mock_response.raise_for_status.return_value = None
        mock_session.return_value.__enter__.return_value.get.return_value = mock_response
        
        show_reviews(config, False)
        
        # Verify console.print was called
        # It calls print(header) then print(no_reviews_panel)
        assert mock_console.print.call_count >= 2
        
        # We can't easily check the content of Rich objects without inspecting them deeply,
        # but we can assume if it didn't crash and called print twice, it likely printed the message.
        # To be more sure, we could inspect the last call.
        args, _ = mock_console.print.call_args_list[-1]
        panel = args[0]
        # Check if "No reviews need your attention" is in the renderable
        from rich.panel import Panel
        assert isinstance(panel, Panel)
        assert "No reviews need your attention" in str(panel.renderable)
