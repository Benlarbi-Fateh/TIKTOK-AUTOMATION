from pathlib import Path

from app.pipeline.context import PipelineContext


class DummyDB:
    def __init__(self):
        self.videos = {}
        self.next_id = 1

    def get_video_by_script(self, script_id):
        for v in self.videos.values():
            if v.get("script_id") == script_id:
                return v
        return None

    def add_video(self, script_id, project_folder=None, audio_path=None, subtitle_path=None, final_video_path=None, status=None):
        vid = {"id": self.next_id, "script_id": script_id, "final_video_path": final_video_path, "platform_id": None, "status": status}
        self.videos[self.next_id] = vid
        self.next_id += 1
        return vid["id"]

    def update_video_publication(self, video_id, platform_id, status="published"):
        v = self.videos.get(video_id)
        if v:
            v["platform_id"] = platform_id
            v["status"] = status


def test_publish_stage_idempotent(monkeypatch, tmp_path):
    # Prepare context with a fake video file
    ctx = PipelineContext()
    video_file = tmp_path / "v.mp4"
    video_file.write_bytes(b"x")
    ctx.current_video = {"path": str(video_file)}
    ctx.current_script = {"script_id": 42, "topic_id": 7}
    ctx.project_folder = tmp_path
    ctx.database = DummyDB()

    # mock PublishClient to avoid real HTTP
    class DummyClient:
        def upload_video(self, file_path, metadata):
            return "upl-1"

        def publish(self, upload_token, idempotency_key=None):
            class R:
                post_id = "post-1"
                status = "published"

            return R()

    monkeypatch.setattr("app.pipeline.stages.publish.PublishClient", lambda api_key=None: DummyClient())

    from app.pipeline.stages.publish import PublishStage

    stage = PublishStage()
    stage.run(ctx)

    # After first run, should be published and DB updated
    assert ctx.settings.get("published") is True
    assert ctx.current_video.get("post_id") == "post-1"

    # Run again: idempotent path should detect existing platform_id and skip
    stage.run(ctx)

    assert ctx.settings.get("published") is True
