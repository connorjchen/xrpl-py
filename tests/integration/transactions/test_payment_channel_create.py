from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import DESTINATION, WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.models.transactions import PaymentChannelCreate


class TestPaymentChannelCreate(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_basic_functionality(self, client):
        payment_channel = await submit_transaction_async(
            PaymentChannelCreate(
                account=WALLET.classic_address,
                sequence=await get_next_valid_seq_number(
                    WALLET.classic_address, client
                ),
                amount="1",
                destination=DESTINATION.classic_address,
                settle_delay=86400,
                public_key=WALLET.public_key,
            ),
            WALLET,
        )
        self.assertTrue(payment_channel.is_successful())
