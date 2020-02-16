#include <stdbool.h>
#include <stdint.h>
#include "qrcodegen.h"

// Text data
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  if (Size < 2)
    return 0;

  uint8_t qr0[qrcodegen_BUFFER_LEN_MAX];
  bool ok = qrcodegen_encodeBinary((uint8_t *) Data, Size, qr0, qrcodegen_Ecc_MEDIUM, qrcodegen_VERSION_MIN, qrcodegen_VERSION_MAX, qrcodegen_Mask_4, true);
  if (!ok)
      return 1;

  return 0;  // Non-zero return values are reserved for future use.
}
