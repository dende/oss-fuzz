#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <iostream>
#include "common.h"

int ZBarcode_Buffer(struct zint_symbol *symbol, int rotate_angle);

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
  if (Size < 2)
    return 0;

  // Add Setup code here.
  struct zint_symbol *my_symbol;my_symbol = ZBarcode_Create();
  if(my_symbol == NULL) {
    printf("Symbol creation failed!\n");
    return 1;
  }
  int symbol_byte = (int) Data[0];
  Data++;
  Size--;

  //create symbology in in range [1, 145] (excluding zero, from BARCODE_CODE11 to BARCODE_RMQR)
  int symbology = (symbol_byte % BARCODE_RMQR) + 1;
/*
  std::cerr << "Symbology: " << symbology << std::endl;
  switch (symbology) {
    case 63:
    case 64:
    case 65:
    case BARCODE_AUSROUTE:
    case BARCODE_AUSREDIRECT:
    case BARCODE_AUSREPLY:
    case BARCODE_UPCA:
    case BARCODE_UPCA_CHK:
    case BARCODE_UPCE:
    case BARCODE_UPCE_CHK:
    case BARCODE_EANX:
    case BARCODE_EANX_CHK:
    case BARCODE_DOTCODE:
    case BARCODE_CODABLOCKF:
    case BARCODE_CODEONE:
    case BARCODE_VIN:
      ZBarcode_Delete(my_symbol);
      return 0;
    default:
      break;
  }
*/
  my_symbol->symbology = symbology;
  unsigned char * input = (unsigned char *) Data;
  ZBarcode_Encode_and_Buffer(my_symbol, input, Size, 0);
  // Add Teardown code here.

  ZBarcode_Delete(my_symbol);

  return 0;
}

