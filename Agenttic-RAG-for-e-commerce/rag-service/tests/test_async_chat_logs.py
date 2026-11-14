import asyncio
from threading import Event

import httpx


def test_slow_log_write_does_not_block_another_chat(client,backend,monkeypatch):
    entered,release=Event(),Event()
    def writer(**values):
        if values["session_id"]=="slow-log":
            entered.set()
            release.wait(timeout=2)
        return True
    monkeypatch.setattr(backend.main,"write_chat_turn",writer)
    async def run():
        transport=httpx.ASGITransport(app=backend.main.app)
        async with httpx.AsyncClient(transport=transport,base_url="http://test") as http:
            first=asyncio.create_task(http.post("/chat",json={"message":"first","session_id":"slow-log"}))
            try:
                assert await asyncio.to_thread(entered.wait,1)
                assert not first.done(),"slow logging blocked event loop until it finished"
                second=await asyncio.wait_for(http.post("/chat",json={"message":"second","session_id":"fast-log"}),timeout=1)
                assert second.status_code==200
                assert second.json()["reply"]=="second"
                assert not first.done()
            finally:
                release.set()
                first_response=await asyncio.wait_for(first,timeout=1)
                assert first_response.status_code==200
    asyncio.run(run())
