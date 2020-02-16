#include <cstdlib>
#include "QrCode.hpp"


extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  if (Size < 2)
    return 0;

  auto ecc_byte = (int) Data[0];
  Data++;Size--;
  qrcodegen::QrCode::Ecc ecl = static_cast<qrcodegen::QrCode::Ecc> (ecc_byte % 5);

  std::vector<uint8_t> dataVector(Data, Data + Size);
  auto qr = qrcodegen::QrCode::encodeBinary(dataVector, ecl);

  return 0;
}

