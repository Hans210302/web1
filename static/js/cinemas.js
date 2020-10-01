$(document).ready(function() {
	$("#chioce-1 li").click(function () {
		$(this).addClass("selected").siblings().removeClass("selected");
		$("#result").html($(this).text())
	});

	$("#chioce-2 li").click(function () {
		$(this).addClass("selected").siblings().removeClass("selected");
		$("#result").html($(this).text())
	});

	$("#chioce-3 li").click(function () {
	    $("#result").html($("input:radio[name='choice']:checked").val());
    });

	$("#chioce li").live("click", function() {
		data1 = $('#result').val();
		html = $.ajax({
			url: "url???",
			type: 'POST',
			data: {data1}
		})
    })
});

