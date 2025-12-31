/*
 * SPDX-FileCopyrightText: 2021-2024 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: CC0-1.0
 */
#define CONFIG_EXAMPLE_LCD_CONTROLLER_SSD1306 1
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_err.h"
#include "esp_log.h"
#include "driver/i2c_master.h"
#include "esp_lvgl_port.h"
#include "lvgl.h"
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

#include "lvgl.h"
#include "stdio.h"

typedef struct
{
    uint16_t cur;
    uint16_t tol;
} score_t;

typedef struct
{
    bool is_finish;
    score_t des;
    score_t mob;
} profile_t;

lv_obj_t *profile_label;
lv_obj_t *bar0;
lv_obj_t *bar1;
lv_obj_t *bar0_inter;
lv_obj_t *bar1_inter;
lv_obj_t *bar0_label;
lv_obj_t *bar1_label;
#define PROFILE_NUM 6
profile_t my_profile[PROFILE_NUM];
bool profile_res[PROFILE_NUM];
uint8_t now_profile = 0;
lv_timer_t *loop_timer;

#define PI 3.1415926

#define CONFIG_EXAMPLE_LCD_CONTROLLER_SSD1306 1
#if CONFIG_EXAMPLE_LCD_CONTROLLER_SH1107
#include "esp_lcd_sh1107.h"
#else
#include "esp_lcd_panel_vendor.h"
#endif

static const char *TAG = "example";

#define I2C_BUS_PORT 0

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//////////////////// Please update the following configuration according to your LCD spec //////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#define EXAMPLE_LCD_PIXEL_CLOCK_HZ (400 * 1000)
#define EXAMPLE_PIN_NUM_SDA 3
#define EXAMPLE_PIN_NUM_SCL 4
#define EXAMPLE_PIN_NUM_RST -1
#define EXAMPLE_I2C_HW_ADDR 0x3c

// The pixel number in horizontal and vertical
#if CONFIG_EXAMPLE_LCD_CONTROLLER_SSD1306
#define EXAMPLE_LCD_H_RES 128
#define EXAMPLE_LCD_V_RES 64
#elif CONFIG_EXAMPLE_LCD_CONTROLLER_SH1107
#define EXAMPLE_LCD_H_RES 64
#define EXAMPLE_LCD_V_RES 128
#endif
// Bit number used to represent command and parameter
#define EXAMPLE_LCD_CMD_BITS 8
#define EXAMPLE_LCD_PARAM_BITS 8

extern void example_lvgl_demo_ui(lv_disp_t *disp);
// SSD1306 单色缓冲区
#define WIDTH 128
#define HEIGHT 64

// SSD1306 单色缓冲区
static uint8_t oled_buf[WIDTH * HEIGHT / 8] = {0};

void my_bar(struct _lv_obj_t *rect, struct _lv_obj_t *rect_inter)
{
    uint8_t my_radius = 6;
    // 外圆角矩形空心线
    lv_obj_set_size(rect, 128, 10);                           // 设置宽高
    lv_obj_set_style_radius(rect, my_radius, 0);              // 圆角半径 10 px
    lv_obj_set_style_border_width(rect, 1, 0);                // 边框宽度
    lv_obj_set_style_border_color(rect, lv_color_black(), 0); // 边框颜色
    lv_obj_set_style_bg_opa(rect, LV_OPA_TRANSP, 0);          // 背景透明

    // 内圆角矩形
    lv_obj_set_size(rect_inter, 124, 6);
    lv_obj_set_style_radius(rect_inter, my_radius, 0);
    lv_obj_set_style_bg_color(rect_inter, lv_color_black(), 0);
    lv_obj_set_style_bg_opa(rect_inter, LV_OPA_COVER, 0);
}

void set_profile_label(struct _lv_obj_t *label)
{
    char buf[32];
    sprintf(buf, "PROFILE %d", 0);
    lv_label_set_text(label, buf);
    /* 对齐方式：顶部水平居中 */
    lv_obj_align(label, LV_ALIGN_TOP_MID, 0, 0);
}

void set_bat_label(struct _lv_obj_t *label, struct _lv_obj_t *last)
{
    char buf[32];
    sprintf(buf, "%d/%d", 110, 120);
    lv_label_set_text(label, buf);
    lv_obj_align_to(label, last, LV_ALIGN_OUT_BOTTOM_RIGHT, 0, 0);
    lv_obj_set_style_text_font(label, &lv_font_montserrat_10, 0);
}

bool check_profile_scores(bool *res)
{
    bool res_total = true;
    for (uint8_t i = 0; i < PROFILE_NUM; i++)
    {
        if (my_profile[i].des.cur < my_profile[i].des.tol)
        {
            my_profile[i].is_finish = false;
            res_total = false;
        }
        else if (my_profile[i].mob.cur < my_profile[i].mob.tol)
        {
            my_profile[i].is_finish = false;
            res_total = false;
        }
        else
        {
            my_profile[i].is_finish = true;
        }

        res[i] = my_profile[i].is_finish;
    }

    return res_total;
}

size_t count_false(const bool arr[], size_t len)
{
    size_t count = 0;
    for (size_t i = 0; i < len; i++)
    {
        if (arr[i] == false)
            count++;
    }
    return count;
}

void update_profile_ui()
{
    bool res = check_profile_scores(profile_res);
    // 若存在未完成的profile，开始刷新UI，否则直接显示profile 0
    if (res)
    {
        now_profile = 0;
        // return;
    }
    else
    {
        // printf("存在未完成的profile\n");
        for (uint8_t i = 0; i < PROFILE_NUM; i++)
        {
            if (my_profile[now_profile].is_finish)
            {
                now_profile++;
                if (now_profile >= PROFILE_NUM)
                {
                    now_profile = 0;
                }
            }
            else
            {
                break;
            }
        }
    }

    printf("now_profile: %d\n", now_profile);

    // 更新名字
    char buf[32];
    sprintf(buf, "PROFILE %d", now_profile);
    lv_label_set_text(profile_label, buf);

    // 更新进度条
    sprintf(buf, "%d/%d", my_profile[now_profile].des.cur, my_profile[now_profile].des.tol);
    lv_label_set_text(bar0_label, buf);
    sprintf(buf, "%d/%d", my_profile[now_profile].mob.cur, my_profile[now_profile].mob.tol);
    lv_label_set_text(bar1_label, buf);

    lv_obj_set_width(bar0_inter, 121 * my_profile[now_profile].des.cur / my_profile[now_profile].des.tol);
    lv_obj_set_width(bar1_inter, 121 * my_profile[now_profile].mob.cur / my_profile[now_profile].mob.tol);

    if (count_false(profile_res, PROFILE_NUM) <= 1)
    {
        printf("未完成的profile <= 1， 不循环\n");
        lv_timer_pause(loop_timer);
    }
    else
    {
        now_profile++;
        if (now_profile >= PROFILE_NUM)
        {
            now_profile = 0;
        }
    }

    // lv_timer_pause(timer);
    // lv_timer_resume(timer);
}

void progress_timer_cb(lv_timer_t *timer)
{
    printf("sdsd\n");
    update_profile_ui();
    // update_bar();

    // lv_timer_del(timer); // 单次执行后删除定时器
}

void example_lvgl_demo_ui(lv_disp_t *disp)
{
    printf("ttttthhhhhiss ttt\n");
    for (uint8_t i = 0; i < PROFILE_NUM; i++)
    {
        my_profile[i].des.cur = 110 + i;
        my_profile[i].des.tol = 180;
        my_profile[i].mob.cur = 120;
        my_profile[i].mob.tol = 120;
    }
    my_profile[2].des.cur = 180;
    my_profile[2].des.tol = 180;
    my_profile[2].mob.cur = 120;
    my_profile[2].mob.tol = 120;

    check_profile_scores(profile_res);
    printf("res:\n");
    for (size_t i = 0; i < PROFILE_NUM; i++)
    {
        printf("%d ", profile_res[i]);
    }
    printf("\n");

    lv_obj_t *scr = lv_disp_get_scr_act(disp);

    // lv_obj_t *label = lv_label_create(scr);
    // lv_label_set_long_mode(label, LV_LABEL_LONG_SCROLL_CIRCULAR); /* Circular scroll */
    // lv_label_set_text(label, "Hello Espressif, Hello LVGL.");
    // /* Size of the screen (if you use rotation 90 or 270, please set disp->driver->ver_res) */
    // lv_obj_set_width(label, disp->driver->hor_res);
    // lv_obj_set_pos(label, 0, 20);

    // 设置标签profile名字
    profile_label = lv_label_create(scr);
    set_profile_label(profile_label);

    // 设置自己写的进度条
    // bar 0
    bar0 = lv_obj_create(scr);
    bar0_inter = lv_obj_create(scr);
    my_bar(bar0, bar0_inter);

    lv_obj_align(bar0, LV_ALIGN_TOP_MID, 0, 18);
    lv_obj_set_pos(bar0_inter, 2, 20);

    bar0_label = lv_label_create(scr);
    set_bat_label(bar0_label, bar0);

    // bar 1
    bar1 = lv_obj_create(scr);
    bar1_inter = lv_obj_create(scr);
    my_bar(bar1, bar1_inter);

    lv_obj_align(bar1, LV_ALIGN_TOP_MID, 0, 40);
    lv_obj_set_pos(bar1_inter, 2, 42);

    bar1_label = lv_label_create(scr);
    set_bat_label(bar1_label, bar1);

    // loop_timer = lv_timer_create(progress_timer_cb, 3000, NULL);
}

void app_main(void)
{
    ESP_LOGI(TAG, "Initialize I2C bus");
    i2c_master_bus_handle_t i2c_bus = NULL;
    i2c_master_bus_config_t bus_config = {
        .clk_source = I2C_CLK_SRC_DEFAULT,
        .glitch_ignore_cnt = 7,
        .i2c_port = I2C_BUS_PORT,
        .sda_io_num = EXAMPLE_PIN_NUM_SDA,
        .scl_io_num = EXAMPLE_PIN_NUM_SCL,
        .flags.enable_internal_pullup = true,
    };
    ESP_ERROR_CHECK(i2c_new_master_bus(&bus_config, &i2c_bus));

    ESP_LOGI(TAG, "Install panel IO");
    esp_lcd_panel_io_handle_t io_handle = NULL;
    esp_lcd_panel_io_i2c_config_t io_config = {
        .dev_addr = EXAMPLE_I2C_HW_ADDR,
        .scl_speed_hz = EXAMPLE_LCD_PIXEL_CLOCK_HZ,
        .control_phase_bytes = 1,               // According to SSD1306 datasheet
        .lcd_cmd_bits = EXAMPLE_LCD_CMD_BITS,   // According to SSD1306 datasheet
        .lcd_param_bits = EXAMPLE_LCD_CMD_BITS, // According to SSD1306 datasheet
#if CONFIG_EXAMPLE_LCD_CONTROLLER_SSD1306
        .dc_bit_offset = 6, // According to SSD1306 datasheet
#elif CONFIG_EXAMPLE_LCD_CONTROLLER_SH1107
        .dc_bit_offset = 0, // According to SH1107 datasheet
        .flags =
            {
                .disable_control_phase = 1,
            }
#endif
    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_i2c(i2c_bus, &io_config, &io_handle));

    ESP_LOGI(TAG, "Install SSD1306 panel driver");
    esp_lcd_panel_handle_t panel_handle = NULL;
    esp_lcd_panel_dev_config_t panel_config = {
        .bits_per_pixel = 1,
        .reset_gpio_num = EXAMPLE_PIN_NUM_RST,
    };
#if CONFIG_EXAMPLE_LCD_CONTROLLER_SSD1306
    esp_lcd_panel_ssd1306_config_t ssd1306_config = {
        .height = EXAMPLE_LCD_V_RES,
    };
    panel_config.vendor_config = &ssd1306_config;
    ESP_ERROR_CHECK(esp_lcd_new_panel_ssd1306(io_handle, &panel_config, &panel_handle));
#elif CONFIG_EXAMPLE_LCD_CONTROLLER_SH1107
    ESP_ERROR_CHECK(esp_lcd_new_panel_sh1107(io_handle, &panel_config, &panel_handle));
#endif

    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel_handle, true));

#if CONFIG_EXAMPLE_LCD_CONTROLLER_SH1107
    ESP_ERROR_CHECK(esp_lcd_panel_invert_color(panel_handle, true));
#endif

    ESP_LOGI(TAG, "Initialize LVGL");
    const lvgl_port_cfg_t lvgl_cfg = ESP_LVGL_PORT_INIT_CONFIG();
    lvgl_port_init(&lvgl_cfg);

    const lvgl_port_display_cfg_t disp_cfg = {
        .io_handle = io_handle,
        .panel_handle = panel_handle,
        .buffer_size = EXAMPLE_LCD_H_RES * EXAMPLE_LCD_V_RES,
        .double_buffer = true,
        .hres = EXAMPLE_LCD_H_RES,
        .vres = EXAMPLE_LCD_V_RES,
        .monochrome = true,
        .rotation = {
            .swap_xy = false,
            .mirror_x = true,
            .mirror_y = true,
        }};
    lv_disp_t *disp = lvgl_port_add_disp(&disp_cfg);

    lv_disp_set_rotation(disp, LV_DISP_ROT_NONE);

    ESP_LOGI(TAG, "Display LVGL Scroll Text");
    // Lock the mutex due to the LVGL APIs are not thread-safe
    if (lvgl_port_lock(0))
    {
        example_lvgl_demo_ui(disp);
        // Release the mutex
        lvgl_port_unlock();
    }
}
