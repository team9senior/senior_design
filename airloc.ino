#include <driver/i2s.h>

//USER SETTINGS 
#define SAMPLE_RATE   44100            // Hz
#define MIC_SPACING   0.05727827       // meters between microphones
#define SPEED_SOUND   343.0            // m/s
#define BUFFER_LEN    1024             // 
#define ENERGY_THRESHOLD 1e7           // 

//I2S PINS 
#define I2S_WS  25
#define I2S_SD  22
#define I2S_SCK 26
#define I2S_PORT I2S_NUM_0

// Buffers
int32_t rawBuffer[BUFFER_LEN];       // interweaved raw samples
float leftBuf[BUFFER_LEN/2];
float rightBuf[BUFFER_LEN/2];

// COMPUTE MAX SHIFT 
int calcMaxShift() {
  float maxDelaySec = MIC_SPACING / SPEED_SOUND;          // max seconds
  float maxSamplesF = maxDelaySec * SAMPLE_RATE;          // max samples
  int maxSamples = (int)ceil(maxSamplesF);
  return maxSamples;
}

// CROSS-CORRELATION 
int computeOffset(float *a, float *b, int n, int maxShift) {
  int bestOffset = 0;
  double bestScore = -1e12;

  for (int shift = -maxShift; shift <= maxShift; shift++) {
    double score = 0;
    for (int i = 0; i < n; i++) {
      int j = i + shift;
      if (j >= 0 && j < n) {
        score += a[i] * b[j];
      }
    }
    if (score > bestScore) {
      bestScore = score;
      bestOffset = shift;
    }
  }

  return bestOffset;
}

//I2S SETUP 
void i2s_install() {
  const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = BUFFER_LEN,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
}

void i2s_setpin() {
  const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = -1,
    .data_in_num = I2S_SD
  };
  i2s_set_pin(I2S_PORT, &pin_config);
}

// SETUP 
void setup() {
  Serial.begin(115200);
  delay(500);

  i2s_install();
  i2s_setpin();
  i2s_start(I2S_PORT);

  Serial.println("TDOA Measurement Started");
  Serial.print("Max shift samples: ");
  Serial.println(calcMaxShift());
}

// LOOP 
void loop() {
  size_t bytesRead = 0;
  // Read interleaved L/R samples from I2S
  i2s_read(I2S_PORT, (void*)rawBuffer, BUFFER_LEN * sizeof(int32_t), &bytesRead, portMAX_DELAY);
  int samplesRead = bytesRead / sizeof(int32_t);

  // Split into left/right
  int pairs = samplesRead / 2;
  for (int i = 0; i < pairs; i++) {
    leftBuf[i] = (float)(rawBuffer[2 * i] >> 11);       // scale down 24-bit to 16-bit
    rightBuf[i] = (float)(rawBuffer[2 * i + 1] >> 11);
  }

  // Compute energy on left channel to detect chirp
  double energy = 0;
  for (int i = 0; i < pairs; i++) {
    energy += leftBuf[i] * leftBuf[i];
  }
  energy /= pairs;

  // Only proceed if energy is above threshold (chirp detected)
  if (energy > ENERGY_THRESHOLD) {
    int maxShift = calcMaxShift();
    int offset = computeOffset(leftBuf, rightBuf, pairs, maxShift);

    // Send offset in samples (one integer per line)
    Serial.println(offset);
  }
  // else, skip sending to MATLAB (no chirp in this buffer)
}