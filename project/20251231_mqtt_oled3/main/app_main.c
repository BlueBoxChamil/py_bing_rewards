/*
 * SPDX-FileCopyrightText: 2022-2023 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_lcd_panel_dev.h"
#include "esp_lcd_panel_ssd1306.h"
#include "esp_err.h"
#include "esp_log.h"
#include "driver/i2c_master.h"
#include "esp_lvgl_port.h"
#include "lvgl.h"
#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include "esp_task_wdt.h"

#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"
#include "esp_log.h"
#include "mqtt_client.h"
#include "cJSON.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_heap_caps.h"

#include "esp_log.h"
#include "mqtt_client.h"
#include "cJSON.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_heap_caps.h"
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_lcd_panel_io.h"
#include "esp_lcd_panel_ops.h"
#include "esp_err.h"
#include "esp_log.h"

#define CONFIG_EXAMPLE_LCD_CONTROLLER_SSD1306 1

#define I2C_BUS_PORT 0
#define EXAMPLE_LCD_PIXEL_CLOCK_HZ (400 * 1000)
// #define EXAMPLE_PIN_NUM_SDA 3
// #define EXAMPLE_PIN_NUM_SCL 4
#define EXAMPLE_PIN_NUM_SDA 4
#define EXAMPLE_PIN_NUM_SCL 5

#define EXAMPLE_PIN_NUM_RST -1
#define EXAMPLE_I2C_HW_ADDR 0x3c
#define EXAMPLE_LCD_CMD_BITS 8
#define EXAMPLE_LCD_PARAM_BITS 8
#define EXAMPLE_LCD_H_RES 128
#define EXAMPLE_LCD_V_RES 64

static const char *TAG = "mqtt5_example";

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
        lv_timer_pause(loop_timer);
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

    lv_obj_set_width(bar0_inter, 124 * my_profile[now_profile].des.cur / my_profile[now_profile].des.tol);
    lv_obj_set_width(bar1_inter, 124 * my_profile[now_profile].mob.cur / my_profile[now_profile].mob.tol);

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

    loop_timer = lv_timer_create(progress_timer_cb, 3000, NULL);
}

void example_lvgl_demo_ui_demo(lv_disp_t *disp)
{
    lv_obj_t *scr = lv_disp_get_scr_act(disp);
    lv_obj_t *label = lv_label_create(scr);
    lv_label_set_long_mode(label, LV_LABEL_LONG_SCROLL_CIRCULAR); /* Circular scroll */
    lv_label_set_text(label, "Hello Espressif, Hello LVGL.");
    /* Size of the screen (if you use rotation 90 or 270, please set disp->driver->ver_res) */
    lv_obj_set_width(label, disp->driver->hor_res);
    lv_obj_align(label, LV_ALIGN_TOP_MID, 0, 0);
}

static void log_error_if_nonzero(const char *message, int error_code)
{
    if (error_code != 0)
    {
        ESP_LOGE(TAG, "Last error %s: 0x%x", message, error_code);
    }
}

static esp_mqtt5_user_property_item_t user_property_arr[] = {
    {"board", "esp32"},
    {"u", "user"},
    {"p", "password"}};

#define USE_PROPERTY_ARR_SIZE sizeof(user_property_arr) / sizeof(esp_mqtt5_user_property_item_t)

static esp_mqtt5_publish_property_config_t publish_property = {
    .payload_format_indicator = 1,
    .message_expiry_interval = 1000,
    .topic_alias = 0,
    .response_topic = "/topic/test/response",
    .correlation_data = "123456",
    .correlation_data_len = 6,
};

static esp_mqtt5_subscribe_property_config_t subscribe_property = {
    .subscribe_id = 25555,
    .no_local_flag = false,
    .retain_as_published_flag = false,
    .retain_handle = 0,
    .is_share_subscribe = true,
    .share_name = "group1",
};

static esp_mqtt5_subscribe_property_config_t subscribe1_property = {
    .subscribe_id = 25555,
    .no_local_flag = true,
    .retain_as_published_flag = false,
    .retain_handle = 0,
};

static esp_mqtt5_unsubscribe_property_config_t unsubscribe_property = {
    .is_share_subscribe = true,
    .share_name = "group1",
};

static esp_mqtt5_disconnect_property_config_t disconnect_property = {
    .session_expiry_interval = 60,
    .disconnect_reason = 0,
};

static void print_user_property(mqtt5_user_property_handle_t user_property)
{
    if (user_property)
    {
        uint8_t count = esp_mqtt5_client_get_user_property_count(user_property);
        if (count)
        {
            esp_mqtt5_user_property_item_t *item = malloc(count * sizeof(esp_mqtt5_user_property_item_t));
            if (esp_mqtt5_client_get_user_property(user_property, item, &count) == ESP_OK)
            {
                for (int i = 0; i < count; i++)
                {
                    esp_mqtt5_user_property_item_t *t = &item[i];
                    ESP_LOGI(TAG, "key is %s, value is %s", t->key, t->value);
                    free((char *)t->key);
                    free((char *)t->value);
                }
            }
            free(item);
        }
    }
}

/*
 * @brief Event handler registered to receive MQTT events
 *
 *  This function is called by the MQTT client event loop.
 *
 * @param handler_args user data registered to the event.
 * @param base Event base for the handler(always MQTT Base in this example).
 * @param event_id The id for the received event.
 * @param event_data The data for the event, esp_mqtt_event_handle_t.
 */
static void mqtt5_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%" PRIi32, base, event_id);
    esp_mqtt_event_handle_t event = event_data;
    esp_mqtt_client_handle_t client = event->client;
    int msg_id;

    ESP_LOGD(TAG, "free heap size is %" PRIu32 ", minimum %" PRIu32, esp_get_free_heap_size(), esp_get_minimum_free_heap_size());
    switch ((esp_mqtt_event_id_t)event_id)
    {
    case MQTT_EVENT_CONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");

        int msg_id = esp_mqtt_client_publish(client, "esp_bing_send", "data_3", 0, 1, 1); // retain=1
        ESP_LOGI(TAG, "Discovery JSON published, msg_id=%d", msg_id);

        esp_mqtt5_client_set_user_property(&subscribe_property.user_property, user_property_arr, USE_PROPERTY_ARR_SIZE);
        esp_mqtt5_client_set_subscribe_property(client, &subscribe_property);
        msg_id = esp_mqtt_client_subscribe(client, "esp_receive_from_pc", 0);
        esp_mqtt5_client_delete_user_property(subscribe_property.user_property);
        subscribe_property.user_property = NULL;
        ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        esp_mqtt5_client_set_user_property(&subscribe_property.user_property, user_property_arr, USE_PROPERTY_ARR_SIZE);
        esp_mqtt5_client_set_subscribe_property(client, &subscribe_property);
        msg_id = esp_mqtt_client_subscribe(client, "esp_receive_from_py", 0);
        esp_mqtt5_client_delete_user_property(subscribe_property.user_property);
        subscribe_property.user_property = NULL;
        ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);

        break;
    case MQTT_EVENT_DISCONNECTED:
        ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        print_user_property(event->property->user_property);
        break;
    case MQTT_EVENT_SUBSCRIBED:
        // ESP_LOGI(TAG, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
        // print_user_property(event->property->user_property);
        // esp_mqtt5_client_set_publish_property(client, &publish_property);
        // msg_id = esp_mqtt_client_publish(client, "esp32_send", "data", 0, 0, 0);
        // ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
        print_user_property(event->property->user_property);
        esp_mqtt5_client_set_user_property(&disconnect_property.user_property, user_property_arr, USE_PROPERTY_ARR_SIZE);
        esp_mqtt5_client_set_disconnect_property(client, &disconnect_property);
        esp_mqtt5_client_delete_user_property(disconnect_property.user_property);
        disconnect_property.user_property = NULL;
        esp_mqtt_client_disconnect(client);
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
        print_user_property(event->property->user_property);
        break;
    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG, "MQTT_EVENT_DATA");
        print_user_property(event->property->user_property);
        ESP_LOGI(TAG, "payload_format_indicator is %d", event->property->payload_format_indicator);
        ESP_LOGI(TAG, "response_topic is %.*s", event->property->response_topic_len, event->property->response_topic);
        ESP_LOGI(TAG, "correlation_data is %.*s", event->property->correlation_data_len, event->property->correlation_data);
        ESP_LOGI(TAG, "content_type is %.*s", event->property->content_type_len, event->property->content_type);
        ESP_LOGI(TAG, "TOPIC=%.*s", event->topic_len, event->topic);
        ESP_LOGI(TAG, "DATA=%.*s", event->data_len, event->data);

        // 判断是否是目标主题
        if (strncmp(event->topic, "esp_receive_from_pc", event->topic_len) == 0)
        {
            // 打印 3
            printf("this is pc msg\n");

            // 解析 JSON,把 JSON 格式的字符串解析成 cJSON 对象
            cJSON *root = cJSON_Parse(event->data);
            if (!root)
            {
                ESP_LOGE(TAG, "JSON parse error");
                return;
            }

            // cJSON *temp_item = cJSON_GetObjectItem(root, "temperature");
            // float temperature = 25.3;
            // if (temp_item && cJSON_IsNumber(temp_item))
            // {
            //     temperature = temp_item->valuedouble;
            //     ESP_LOGI(TAG, "Received temperature: %.2f", temperature);
            // }

            for (int i = 0; i < PROFILE_NUM; i++)
            {
                char key[16];
                snprintf(key, sizeof(key), "profile_%d", i);

                cJSON *arr = cJSON_GetObjectItem(root, key);
                if (!cJSON_IsArray(arr) || cJSON_GetArraySize(arr) != 4)
                {
                    ESP_LOGW("JSON", "%s invalid", key);
                    continue;
                }

                cJSON *item;
                item = cJSON_GetArrayItem(arr, 0);
                my_profile[i].des.cur = item->valueint;
                item = cJSON_GetArrayItem(arr, 1);
                my_profile[i].des.tol = item->valueint;
                item = cJSON_GetArrayItem(arr, 2);
                my_profile[i].mob.cur = item->valueint;
                item = cJSON_GetArrayItem(arr, 3);
                my_profile[i].mob.tol = item->valueint;
            }

            cJSON_Delete(root);

            for (uint8_t i = 0; i < PROFILE_NUM; i++)
            {
                printf("%03d, %03d, %03d, %03d\n", my_profile[i].des.cur, my_profile[i].des.tol, my_profile[i].mob.cur, my_profile[i].mob.tol);
            }
            lv_timer_resume(loop_timer);
        }
        else if (strncmp(event->topic, "esp_receive_from_py", event->topic_len) == 0)
        {
            // 打印 3
            printf("this is py msg\n");

            // 解析 JSON,把 JSON 格式的字符串解析成 cJSON 对象
            cJSON *root = cJSON_Parse(event->data);
            if (!root)
            {
                ESP_LOGE(TAG, "JSON parse error");
                return;
            }

            // cJSON *temp_item = cJSON_GetObjectItem(root, "temperature");
            // float temperature = 25.3;
            // if (temp_item && cJSON_IsNumber(temp_item))
            // {
            //     temperature = temp_item->valuedouble;
            //     ESP_LOGI(TAG, "Received temperature: %.2f", temperature);
            // }

            for (int i = 0; i < PROFILE_NUM; i++)
            {
                char key[16];
                snprintf(key, sizeof(key), "profile_%d", i);

                cJSON *arr = cJSON_GetObjectItem(root, key);
                if (!cJSON_IsArray(arr) || cJSON_GetArraySize(arr) != 4)
                {
                    ESP_LOGW("JSON", "%s invalid", key);
                    continue;
                }

                cJSON *item;
                item = cJSON_GetArrayItem(arr, 0);
                my_profile[i].des.cur = item->valueint;
                item = cJSON_GetArrayItem(arr, 1);
                my_profile[i].des.tol = item->valueint;
                item = cJSON_GetArrayItem(arr, 2);
                my_profile[i].mob.cur = item->valueint;
                item = cJSON_GetArrayItem(arr, 3);
                my_profile[i].mob.tol = item->valueint;
            }

            cJSON_Delete(root);

            for (uint8_t i = 0; i < PROFILE_NUM; i++)
            {
                printf("%03d, %03d, %03d, %03d\n", my_profile[i].des.cur, my_profile[i].des.tol, my_profile[i].mob.cur, my_profile[i].mob.tol);
            }
            lv_timer_resume(loop_timer);
        }
        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        print_user_property(event->property->user_property);
        ESP_LOGI(TAG, "MQTT5 return code is %d", event->error_handle->connect_return_code);
        if (event->error_handle->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT)
        {
            log_error_if_nonzero("reported from esp-tls", event->error_handle->esp_tls_last_esp_err);
            log_error_if_nonzero("reported from tls stack", event->error_handle->esp_tls_stack_err);
            log_error_if_nonzero("captured as transport's socket errno", event->error_handle->esp_transport_sock_errno);
            ESP_LOGI(TAG, "Last errno string (%s)", strerror(event->error_handle->esp_transport_sock_errno));
        }
        break;
    default:
        ESP_LOGI(TAG, "Other event id:%d", event->event_id);
        break;
    }
}

static void mqtt5_app_start(void)
{
    esp_mqtt5_connection_property_config_t connect_property = {
        .session_expiry_interval = 10,
        .maximum_packet_size = 1024,
        .receive_maximum = 65535,
        .topic_alias_maximum = 2,
        .request_resp_info = true,
        .request_problem_info = true,
        .will_delay_interval = 10,
        .payload_format_indicator = true,
        .message_expiry_interval = 10,
        .response_topic = "/test/response",
        .correlation_data = "123456",
        .correlation_data_len = 6,
    };

    esp_mqtt_client_config_t mqtt5_cfg = {
        .broker.address.uri = CONFIG_BROKER_URL,
        .session.protocol_ver = MQTT_PROTOCOL_V_5,
        // .network.disable_auto_reconnect = true,
        .credentials.username = "esp_bing",
        .credentials.authentication.password = "wx123456",
        .session.last_will.topic = "/topic/will",
        .session.last_will.msg = "i will leave",
        .session.last_will.msg_len = 12,
        .session.last_will.qos = 1,
        .session.last_will.retain = true,
        .network.disable_auto_reconnect = false,
        .network.reconnect_timeout_ms = 5000
    };

#if CONFIG_BROKER_URL_FROM_STDIN
    char line[128];

    if (strcmp(mqtt5_cfg.uri, "FROM_STDIN") == 0)
    {
        int count = 0;
        printf("Please enter url of mqtt broker\n");
        while (count < 128)
        {
            int c = fgetc(stdin);
            if (c == '\n')
            {
                line[count] = '\0';
                break;
            }
            else if (c > 0 && c < 127)
            {
                line[count] = c;
                ++count;
            }
            vTaskDelay(10 / portTICK_PERIOD_MS);
        }
        mqtt5_cfg.broker.address.uri = line;
        printf("Broker url: %s\n", line);
    }
    else
    {
        ESP_LOGE(TAG, "Configuration mismatch: wrong broker url");
        abort();
    }
#endif /* CONFIG_BROKER_URL_FROM_STDIN */

    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&mqtt5_cfg);

    /* Set connection properties and user properties */
    esp_mqtt5_client_set_user_property(&connect_property.user_property, user_property_arr, USE_PROPERTY_ARR_SIZE);
    esp_mqtt5_client_set_user_property(&connect_property.will_user_property, user_property_arr, USE_PROPERTY_ARR_SIZE);
    esp_mqtt5_client_set_connect_property(client, &connect_property);

    /* If you call esp_mqtt5_client_set_user_property to set user properties, DO NOT forget to delete them.
     * esp_mqtt5_client_set_connect_property will malloc buffer to store the user_property and you can delete it after
     */
    esp_mqtt5_client_delete_user_property(connect_property.user_property);
    esp_mqtt5_client_delete_user_property(connect_property.will_user_property);

    /* The last argument may be used to pass data to the event handler, in this example mqtt_event_handler */
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt5_event_handler, NULL);
    esp_mqtt_client_start(client);
}

static void mem_monitor_task(void *arg)
{
    while (1)
    {
        size_t free_heap = esp_get_free_heap_size();
        size_t min_free = esp_get_minimum_free_heap_size();
        size_t internal = heap_caps_get_free_size(MALLOC_CAP_INTERNAL);

        // ESP_LOGI("MEM",
        //          "free=%u, min=%u, internal=%u",
        //          free_heap, min_free, internal);
        printf("%u,%u,%u\n",
               free_heap, min_free, internal);

        vTaskDelay(pdMS_TO_TICKS(1000)); // 1s
    }
}

void lvgl_task(void *arg)
{
    esp_task_wdt_delete(NULL); // 调试时删除 WDT

    lv_disp_t *disp = (lv_disp_t *)arg;

    // 初始化 UI
    if (lvgl_port_lock(0))
    {
        example_lvgl_demo_ui(disp);
        lvgl_port_unlock();
    }

    // 循环刷新 LVGL
    while (1)
    {
        if (lvgl_port_lock(0))
        {
            lv_timer_handler(); // 或 lv_task_handler() 根据 LVGL 版本
            lvgl_port_unlock();
        }
        vTaskDelay(pdMS_TO_TICKS(20));
    }
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
        .dc_bit_offset = 6,                     // According to SSD1306 datasheet

    };
    ESP_ERROR_CHECK(esp_lcd_new_panel_io_i2c(i2c_bus, &io_config, &io_handle));

    ESP_LOGI(TAG, "Install SSD1306 panel driver");
    esp_lcd_panel_handle_t panel_handle = NULL;
    esp_lcd_panel_dev_config_t panel_config = {
        .bits_per_pixel = 1,
        .reset_gpio_num = EXAMPLE_PIN_NUM_RST,
    };

    esp_lcd_panel_ssd1306_config_t ssd1306_config = {
        .height = EXAMPLE_LCD_V_RES,
    };
    panel_config.vendor_config = &ssd1306_config;
    ESP_ERROR_CHECK(esp_lcd_new_panel_ssd1306(io_handle, &panel_config, &panel_handle));

    ESP_ERROR_CHECK(esp_lcd_panel_reset(panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_init(panel_handle));
    ESP_ERROR_CHECK(esp_lcd_panel_disp_on_off(panel_handle, true));

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
            .mirror_x = false,
            .mirror_y = false,
        }};
    lv_disp_t *disp = lvgl_port_add_disp(&disp_cfg);

    lv_disp_set_rotation(disp, LV_DISP_ROT_180);

    ESP_LOGI(TAG, "Display LVGL Scroll Text");
    // Lock the mutex due to the LVGL APIs are not thread-safe
    // if (lvgl_port_lock(0))
    // {
    //     example_lvgl_demo_ui(disp);
    //     // Release the mutex
    //     lvgl_port_unlock();
    // }

    xTaskCreate(lvgl_task, "lvgl_task", 4096 * 6, disp, 3, NULL);

    ESP_LOGI(TAG, "[APP] Startup..");
    ESP_LOGI(TAG, "[APP] Free memory: %" PRIu32 " bytes", esp_get_free_heap_size());
    ESP_LOGI(TAG, "[APP] IDF version: %s", esp_get_idf_version());

    esp_log_level_set("*", ESP_LOG_INFO);
    esp_log_level_set("mqtt_client", ESP_LOG_VERBOSE);
    esp_log_level_set("mqtt_example", ESP_LOG_VERBOSE);
    esp_log_level_set("transport_base", ESP_LOG_VERBOSE);
    esp_log_level_set("esp-tls", ESP_LOG_VERBOSE);
    esp_log_level_set("transport", ESP_LOG_VERBOSE);
    esp_log_level_set("outbox", ESP_LOG_VERBOSE);

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
     * Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    ESP_ERROR_CHECK(example_connect());

    mqtt5_app_start();
}
