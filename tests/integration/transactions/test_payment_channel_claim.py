from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import submit_transaction_async, test_async_and_sync
from tests.integration.reusable_values import PAYMENT_CHANNEL, WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.models.transactions import PaymentChannelClaim


class TestPaymentChannelClaim(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_receiver_claim(self, client):
        response = await submit_transaction_async(
            PaymentChannelClaim(
                account=WALLET.classic_address,
                sequence=await get_next_valid_seq_number(
                    WALLET.classic_address, client
                ),
                channel=PAYMENT_CHANNEL.result["tx_json"]["hash"],
            ),
            WALLET,
        )
        self.assertTrue(response.is_successful())
