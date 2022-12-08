from tests.integration.integration_test_case import IntegrationTestCase
from tests.integration.it_utils import test_async_and_sync
from tests.integration.reusable_values import WALLET
from xrpl.asyncio.account import get_next_valid_seq_number
from xrpl.asyncio.transaction import (
    safe_sign_and_autofill_transaction as safe_sign_and_autofill_transaction_async,
)
from xrpl.core.binarycodec import encode
from xrpl.models.amounts import IssuedCurrencyAmount
from xrpl.models.requests import SubmitOnly
from xrpl.models.transactions import OfferCreate


class TestSubmitOnly(IntegrationTestCase):
    @test_async_and_sync(globals(), ["xrpl.account.get_next_valid_seq_number"])
    async def test_basic_functionality(self, client):
        TX = OfferCreate(
            account=WALLET.classic_address,
            sequence=await get_next_valid_seq_number(WALLET.classic_address, client),
            last_ledger_sequence=await get_next_valid_seq_number(
                WALLET.classic_address, client
            )
            + 10,
            taker_gets="13100000",
            taker_pays=IssuedCurrencyAmount(
                currency="USD",
                issuer=WALLET.classic_address,
                value="10",
            ),
        )
        transaction = await safe_sign_and_autofill_transaction_async(TX, WALLET, client)
        tx_json = transaction.to_xrpl()
        tx_blob = encode(tx_json)
        response = await client.request(
            SubmitOnly(
                tx_blob=tx_blob,
            )
        )
        self.assertTrue(response.is_successful())
