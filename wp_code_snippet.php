<?php
function compression_api_on_uploads($metadata) {
  global $wpdb;
  // Get attachment ID of uploaded image
  $file = $metadata['file'];
  error_log(print_r(wp_get_upload_dir()['url'].'/'.$file, true));
  $ext = array(".png", ".jpg", ".gif", ".jpeg");
  $file_no_ext = str_replace($ext, "", $file);

  //Setup curl request
  $endpoint = wp_get_upload_dir()['url'] . '/' . $file;
  $params = array(
    'url' => $endpoint,
  );
  $url = 'https://emc-endpoint.herokuapp.com/?' . http_build_query($params);

  //curl request to query API
  $ch = curl_init($url);
  $optArray = array(
    CURLOPT_RETURNTRANSFER => true
  );
  curl_setopt_array($ch, $optArray);
  $response = json_decode(curl_exec($ch));
  $image64 = $response->image64;
  $extension = $response->ext;
  curl_close($ch);

  //decode image from base64
  file_put_contents(wp_get_upload_dir()['basedir']. '/' . $file_no_ext . $extension, base64_decode($image64));
  return $metadata;
}
add_filter('wp_generate_attachment_metadata','compression_api_on_uploads');
