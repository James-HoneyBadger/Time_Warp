use eframe::egui;
use time_warp_ide::app::TimeWarpApp;

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions {
        viewport: egui::ViewportBuilder::default()
            .with_inner_size([1200.0, 800.0])
            .with_title("Time Warp IDE"),
        ..Default::default()
    };

    eframe::run_native(
        "Time Warp IDE",
        options,
        Box::new(|_cc| Box::new(TimeWarpApp::default())),
    )
}
